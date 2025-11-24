# Unreal Engine 5 Integration Guide for Student Educational RAG Agent

This guide explains how to integrate the Student Educational RAG Agent into Unreal Engine 5, enabling students to interact with the agent directly from within a game or educational application.

## Overview

The integration allows Unreal Engine 5 to:
- Send student questions to the RAG agent
- Receive answers with citations
- Maintain conversation context (board, grade, subject)
- Handle multiple students with different contexts
- Display educational content in-game

## Architecture

```
Unreal Engine 5
    ↓ (HTTP/HTTPS)
Vertex AI Agent Engine API
    ↓
Student Educational RAG Agent
    ↓
Vertex AI RAG Engine (Textbooks)
```

## Prerequisites

1. **Deployed Agent:** The agent must be deployed to Vertex AI Agent Engine
   ```bash
   uv run python deployment/deploy.py
   ```

2. **Google Cloud Setup:**
   - GCP Project with Vertex AI enabled
   - Service Account with appropriate permissions
   - RAG Corpus with textbooks uploaded

3. **Unreal Engine 5:**
   - Version 5.0 or later
   - HTTP plugin enabled
   - JSON plugin enabled

## Integration Methods

### Method 1: HTTP REST API Integration (Recommended)

This method uses HTTP requests to communicate with the deployed agent.

#### Step 1: Create Unreal Engine Plugin Structure

Create a plugin directory structure:
```
Plugins/
└── StudentRAGAgent/
    ├── Source/
    │   └── StudentRAGAgent/
    │       ├── StudentRAGAgent.Build.cs
    │       ├── StudentRAGAgent.h
    │       ├── StudentRAGAgent.cpp
    │       ├── RAGAgentAPI.h
    │       ├── RAGAgentAPI.cpp
    │       ├── RAGSessionManager.h
    │       └── RAGSessionManager.cpp
    └── StudentRAGAgent.uplugin
```

#### Step 2: Plugin Descriptor (StudentRAGAgent.uplugin)

```json
{
  "FileVersion": 3,
  "Version": 1,
  "VersionName": "1.0",
  "FriendlyName": "Student RAG Agent",
  "Description": "Integration with Student Educational RAG Agent for Vertex AI",
  "Category": "Education",
  "CreatedBy": "Your Name",
  "CreatedByURL": "",
  "DocsURL": "",
  "MarketplaceURL": "",
  "SupportURL": "",
  "EngineVersion": "5.0.0",
  "CanContainContent": true,
  "IsBetaVersion": false,
  "IsExperimentalVersion": false,
  "EnabledByDefault": true,
  "CanBeUsedWithUnrealHeaderTool": true,
  "Modules": [
    {
      "Name": "StudentRAGAgent",
      "Type": "Runtime",
      "LoadingPhase": "Default"
    }
  ],
  "Plugins": [
    {
      "Name": "HTTP",
      "Enabled": true
    },
    {
      "Name": "Json",
      "Enabled": true
    }
  ]
}
```

#### Step 3: Build File (StudentRAGAgent.Build.cs)

```csharp
using UnrealBuildTool;

public class StudentRAGAgent : ModuleRules
{
    public StudentRAGAgent(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "HTTP",
            "Json",
            "JsonUtilities"
        });
        
        PrivateDependencyModuleNames.AddRange(new string[] {
            "Slate",
            "SlateCore"
        });
    }
}
```

#### Step 4: RAG Agent API Header (RAGAgentAPI.h)

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Http.h"
#include "Dom/JsonObject.h"
#include "RAGAgentAPI.generated.h"

USTRUCT(BlueprintType)
struct FStudentContext
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    FString EducationBoard; // e.g., "CBSE", "ICSE", "Tamil Nadu State Board"

    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    FString Grade; // e.g., "Grade 10", "Class 9", "Grade 4"

    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    FString Subject; // e.g., "Science", "Mathematics", "English"
};

USTRUCT(BlueprintType)
struct FAgentResponse
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    FString Text;

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> Citations;

    UPROPERTY(BlueprintReadWrite)
    bool bSuccess;

    UPROPERTY(BlueprintReadWrite)
    FString ErrorMessage;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAgentResponse, const FAgentResponse&, Response, bool, bSuccess);

UCLASS(BlueprintType, Blueprintable)
class STUDENTRAGAGENT_API URAGAgentAPI : public UObject
{
    GENERATED_BODY()

public:
    URAGAgentAPI();

    // Initialize the API with project credentials
    UFUNCTION(BlueprintCallable, Category = "RAG Agent")
    void Initialize(const FString& ProjectID, const FString& Location, const FString& AgentEngineID);

    // Create a new session for a student
    UFUNCTION(BlueprintCallable, Category = "RAG Agent")
    void CreateSession(const FString& UserID);

    // Send a question to the agent
    UFUNCTION(BlueprintCallable, Category = "RAG Agent")
    void SendQuestion(const FString& Question, const FStudentContext& Context);

    // Send a question with context already set
    UFUNCTION(BlueprintCallable, Category = "RAG Agent")
    void SendQuestionWithContext(const FString& Question);

    // Set student context (board, grade, subject)
    UFUNCTION(BlueprintCallable, Category = "RAG Agent")
    void SetStudentContext(const FStudentContext& Context);

    // Get current student context
    UFUNCTION(BlueprintPure, Category = "RAG Agent")
    FStudentContext GetStudentContext() const { return CurrentContext; }

    // Event fired when agent responds
    UPROPERTY(BlueprintAssignable, Category = "RAG Agent")
    FOnAgentResponse OnAgentResponse;

private:
    FString ProjectID;
    FString Location;
    FString AgentEngineID;
    FString AccessToken;
    FString SessionID;
    FString UserID;
    FStudentContext CurrentContext;

    void GetAccessToken();
    void OnAccessTokenReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
    void OnSessionCreated(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
    void OnQuestionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
    FString BuildQueryMessage(const FString& Question, const FStudentContext& Context);
    FAgentResponse ParseAgentResponse(const FString& ResponseBody);
};
```

#### Step 5: RAG Agent API Implementation (RAGAgentAPI.cpp)

```cpp
#include "RAGAgentAPI.h"
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

URAGAgentAPI::URAGAgentAPI()
{
    // Initialize HTTP module
    FHttpModule::Get();
}

void URAGAgentAPI::Initialize(const FString& InProjectID, const FString& InLocation, const FString& InAgentEngineID)
{
    ProjectID = InProjectID;
    Location = InLocation;
    AgentEngineID = InAgentEngineID;
    
    // Get access token
    GetAccessToken();
}

void URAGAgentAPI::GetAccessToken()
{
    // For production, use service account or OAuth flow
    // For development, you can use gcloud auth print-access-token
    // This is a simplified version - implement proper OAuth in production
    
    FString TokenPath = FPaths::Combine(FPaths::ProjectDir(), TEXT("Config"), TEXT("gcloud_token.txt"));
    if (FPaths::FileExists(TokenPath))
    {
        FFileHelper::LoadFileToString(AccessToken, *TokenPath);
        AccessToken = AccessToken.TrimStartAndEnd();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Access token not found. Please set up authentication."));
    }
}

void URAGAgentAPI::CreateSession(const FString& InUserID)
{
    UserID = InUserID;
    
    if (AccessToken.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Access token not available. Cannot create session."));
        return;
    }

    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
    
    FString URL = FString::Printf(TEXT("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/sessions"),
        *Location, *ProjectID, *Location);
    
    Request->SetURL(URL);
    Request->SetVerb(TEXT("POST"));
    Request->SetHeader(TEXT("Authorization"), FString::Printf(TEXT("Bearer %s"), *AccessToken));
    Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
    
    // Create request body
    TSharedPtr<FJsonObject> RequestObj = MakeShareable(new FJsonObject);
    RequestObj->SetStringField(TEXT("app_name"), AgentEngineID);
    RequestObj->SetStringField(TEXT("user_id"), UserID);
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(RequestObj.ToSharedRef(), Writer);
    
    Request->SetContentAsString(OutputString);
    Request->OnProcessRequestComplete().BindUObject(this, &URAGAgentAPI::OnSessionCreated);
    Request->ProcessRequest();
}

void URAGAgentAPI::OnSessionCreated(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
    if (bWasSuccessful && Response.IsValid() && Response->GetResponseCode() == 200)
    {
        TSharedPtr<FJsonObject> JsonObject;
        TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());
        
        if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
        {
            SessionID = JsonObject->GetStringField(TEXT("id"));
            UE_LOG(LogTemp, Log, TEXT("Session created: %s"), *SessionID);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create session. Response: %s"), 
            Response.IsValid() ? *Response->GetContentAsString() : TEXT("No response"));
    }
}

void URAGAgentAPI::SetStudentContext(const FStudentContext& Context)
{
    CurrentContext = Context;
}

void URAGAgentAPI::SendQuestion(const FString& Question, const FStudentContext& Context)
{
    CurrentContext = Context;
    SendQuestionWithContext(Question);
}

void URAGAgentAPI::SendQuestionWithContext(const FString& Question)
{
    if (SessionID.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("Session not created. Creating session..."));
        CreateSession(UserID.IsEmpty() ? TEXT("student_001") : UserID);
        // Note: In production, wait for session creation callback
        return;
    }

    if (AccessToken.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Access token not available."));
        return;
    }

    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
    
    FString URL = FString::Printf(TEXT("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/reasoningEngines/%s:query"),
        *Location, *ProjectID, *Location, *AgentEngineID);
    
    Request->SetURL(URL);
    Request->SetVerb(TEXT("POST"));
    Request->SetHeader(TEXT("Authorization"), FString::Printf(TEXT("Bearer %s"), *AccessToken));
    Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
    
    // Build query message with context
    FString QueryMessage = BuildQueryMessage(Question, CurrentContext);
    
    // Create request body
    TSharedPtr<FJsonObject> RequestObj = MakeShareable(new FJsonObject);
    RequestObj->SetStringField(TEXT("user_id"), UserID);
    RequestObj->SetStringField(TEXT("session_id"), SessionID);
    RequestObj->SetStringField(TEXT("message"), QueryMessage);
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(RequestObj.ToSharedRef(), Writer);
    
    Request->SetContentAsString(OutputString);
    Request->OnProcessRequestComplete().BindUObject(this, &URAGAgentAPI::OnQuestionResponse);
    Request->ProcessRequest();
}

FString URAGAgentAPI::BuildQueryMessage(const FString& Question, const FStudentContext& Context)
{
    // If context is provided, include it in the message
    if (!Context.EducationBoard.IsEmpty() && !Context.Grade.IsEmpty() && !Context.Subject.IsEmpty())
    {
        return FString::Printf(TEXT("I'm studying %s %s %s. %s"),
            *Context.EducationBoard, *Context.Grade, *Context.Subject, *Question);
    }
    return Question;
}

void URAGAgentAPI::OnQuestionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
    FAgentResponse AgentResponse;
    
    if (bWasSuccessful && Response.IsValid() && Response->GetResponseCode() == 200)
    {
        FString ResponseBody = Response->GetContentAsString();
        AgentResponse = ParseAgentResponse(ResponseBody);
        AgentResponse.bSuccess = true;
    }
    else
    {
        AgentResponse.bSuccess = false;
        AgentResponse.ErrorMessage = Response.IsValid() ? Response->GetContentAsString() : TEXT("No response");
        UE_LOG(LogTemp, Error, TEXT("Failed to get agent response: %s"), *AgentResponse.ErrorMessage);
    }
    
    // Broadcast the response
    OnAgentResponse.Broadcast(AgentResponse, AgentResponse.bSuccess);
}

FAgentResponse URAGAgentAPI::ParseAgentResponse(const FString& ResponseBody)
{
    FAgentResponse Response;
    Response.bSuccess = false;
    
    TSharedPtr<FJsonObject> JsonObject;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(ResponseBody);
    
    if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
    {
        // Parse response structure
        if (JsonObject->HasField(TEXT("response")))
        {
            TSharedPtr<FJsonObject> ResponseObj = JsonObject->GetObjectField(TEXT("response"));
            
            if (ResponseObj->HasField(TEXT("content")))
            {
                TSharedPtr<FJsonObject> ContentObj = ResponseObj->GetObjectField(TEXT("content"));
                
                if (ContentObj->HasField(TEXT("parts")))
                {
                    TArray<TSharedPtr<FJsonValue>> PartsArray = ContentObj->GetArrayField(TEXT("parts"));
                    
                    for (const TSharedPtr<FJsonValue>& PartValue : PartsArray)
                    {
                        TSharedPtr<FJsonObject> PartObj = PartValue->AsObject();
                        if (PartObj->HasField(TEXT("text")))
                        {
                            Response.Text += PartObj->GetStringField(TEXT("text"));
                        }
                    }
                }
            }
            
            // Parse citations if available
            if (ResponseObj->HasField(TEXT("citations")))
            {
                TArray<TSharedPtr<FJsonValue>> CitationsArray = ResponseObj->GetArrayField(TEXT("citations"));
                for (const TSharedPtr<FJsonValue>& CitationValue : CitationsArray)
                {
                    TSharedPtr<FJsonObject> CitationObj = CitationValue->AsObject();
                    if (CitationObj->HasField(TEXT("title")))
                    {
                        Response.Citations.Add(CitationObj->GetStringField(TEXT("title")));
                    }
                }
            }
            
            Response.bSuccess = true;
        }
    }
    
    return Response;
}
```

### Method 2: Blueprint Integration

Create Blueprint classes that wrap the C++ API for easier use in Blueprints.

#### Blueprint: BP_RAGAgentManager

1. Create a Blueprint class based on `URAGAgentAPI`
2. Add Blueprint nodes for:
   - Initialize Agent
   - Set Student Context
   - Ask Question
   - Handle Response

#### Example Blueprint Usage:

```
Event BeginPlay
    → Initialize Agent (ProjectID, Location, AgentEngineID)
    → Create Session (UserID)
    
On Button Click (Ask Question)
    → Set Student Context (Board: "CBSE", Grade: "Grade 10", Subject: "Science")
    → Send Question ("What is photosynthesis?")
    
On Agent Response
    → Display Text in UI
    → Show Citations
```

### Method 3: Widget UI Integration

Create a UI widget for student interaction.

#### Widget Blueprint: WBP_StudentRAGChat

**Components:**
- Text Input Box (for questions)
- Scrollable Text Box (for responses)
- Context Selection (Board, Grade, Subject dropdowns)
- Send Button
- Citations Display

**Blueprint Logic:**
```cpp
// On Send Button Clicked
void OnSendButtonClicked()
{
    FString Question = QuestionInputBox->GetText().ToString();
    FStudentContext Context;
    Context.EducationBoard = BoardDropdown->GetSelectedOption();
    Context.Grade = GradeDropdown->GetSelectedOption();
    Context.Subject = SubjectDropdown->GetSelectedOption();
    
    RAGAgentAPI->SendQuestion(Question, Context);
}

// On Agent Response
void OnAgentResponseReceived(const FAgentResponse& Response, bool bSuccess)
{
    if (bSuccess)
    {
        ResponseTextBox->SetText(FText::FromString(Response.Text));
        
        // Display citations
        FString CitationsText = TEXT("Citations:\n");
        for (const FString& Citation : Response.Citations)
        {
            CitationsText += FString::Printf(TEXT("- %s\n"), *Citation);
        }
        CitationsTextBox->SetText(FText::FromString(CitationsText));
    }
}
```

## Configuration

### Step 1: Create Configuration File

Create `Config/DefaultRAGAgent.ini`:

```ini
[RAGAgent]
ProjectID=your-project-id
Location=us-central1
AgentEngineID=projects/123/locations/us-central1/reasoningEngines/456
DefaultUserID=student_001
```

### Step 2: Load Configuration in C++

```cpp
void URAGAgentAPI::LoadConfiguration()
{
    FString ConfigPath = FPaths::Combine(FPaths::ProjectConfigDir(), TEXT("DefaultRAGAgent.ini"));
    // Load configuration values
}
```

## Authentication Setup

### Option 1: Service Account (Recommended for Production)

1. Create a service account in GCP
2. Download JSON key
3. Store securely in Unreal (use encrypted storage)
4. Use service account for authentication

### Option 2: OAuth 2.0 Flow

Implement OAuth 2.0 flow for user authentication.

### Option 3: Access Token File (Development Only)

For development, save access token to file:
```bash
gcloud auth print-access-token > Config/gcloud_token.txt
```

## Example Usage in Game

### Scenario: Educational Game with RAG Agent

```cpp
// In your game character class
class AStudentCharacter : public ACharacter
{
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class URAGAgentAPI* RAGAgent;
    
    void BeginPlay() override
    {
        // Initialize RAG Agent
        RAGAgent = NewObject<URAGAgentAPI>(this);
        RAGAgent->Initialize(ProjectID, Location, AgentEngineID);
        RAGAgent->CreateSession(GetPlayerID());
        
        // Set student context
        FStudentContext Context;
        Context.EducationBoard = TEXT("CBSE");
        Context.Grade = TEXT("Grade 10");
        Context.Subject = TEXT("Science");
        RAGAgent->SetStudentContext(Context);
        
        // Bind response handler
        RAGAgent->OnAgentResponse.AddDynamic(this, &AStudentCharacter::OnRAGResponse);
    }
    
    UFUNCTION()
    void AskQuestion(const FString& Question)
    {
        RAGAgent->SendQuestionWithContext(Question);
    }
    
    UFUNCTION()
    void OnRAGResponse(const FAgentResponse& Response, bool bSuccess)
    {
        if (bSuccess)
        {
            // Display response in game UI
            DisplayAnswer(Response.Text, Response.Citations);
        }
    }
};
```

## Features Included

✅ **Context Management:** Set and remember student's board, grade, and subject  
✅ **Session Management:** Maintain conversation context across questions  
✅ **RAG Retrieval:** Automatic retrieval from appropriate textbooks  
✅ **Citations:** Display source citations with answers  
✅ **Multiple Students:** Support different students with different contexts  
✅ **Error Handling:** Proper error messages and retry logic  
✅ **Blueprint Support:** Full Blueprint integration for non-programmers  

## Testing

### Test in Editor

1. Create a test level
2. Add RAG Agent Manager actor
3. Configure with your credentials
4. Test questions in Play mode

### Test Scenarios

```cpp
// Test 1: Question with context
SetContext("CBSE", "Grade 10", "Science");
SendQuestion("What is photosynthesis?");

// Test 2: Question without context
SendQuestion("What is a quadratic equation?");

// Test 3: Follow-up question (context remembered)
SendQuestion("What about cellular respiration?");

// Test 4: Different student
CreateSession("student_002");
SetContext("ICSE", "Class 9", "Mathematics");
SendQuestion("What is algebra?");
```

## Performance Considerations

1. **Async Operations:** All HTTP calls are asynchronous
2. **Caching:** Consider caching common questions
3. **Rate Limiting:** Implement rate limiting for API calls
4. **Connection Pooling:** Reuse HTTP connections
5. **Error Retry:** Implement exponential backoff for retries

## Security Best Practices

1. **Never hardcode credentials** in source code
2. **Use encrypted storage** for tokens
3. **Validate all inputs** before sending to API
4. **Implement rate limiting** to prevent abuse
5. **Use HTTPS** for all API calls
6. **Rotate access tokens** regularly

## Troubleshooting

### Issue: Access Token Expired
**Solution:** Implement token refresh logic or use service account

### Issue: Session Not Created
**Solution:** Check network connectivity and API permissions

### Issue: No Response from Agent
**Solution:** Verify agent is deployed and RAG corpus is accessible

### Issue: Wrong Context Used
**Solution:** Ensure SetStudentContext is called before SendQuestion

## Additional Resources

- [Unreal Engine HTTP Plugin Documentation](https://docs.unrealengine.com/5.0/en-US/http-plugin-in-unreal-engine/)
- [Unreal Engine JSON Plugin](https://docs.unrealengine.com/5.0/en-US/json-in-unreal-engine/)
- [Vertex AI Agent Engine API](https://cloud.google.com/vertex-ai/docs/agent-engine/overview)

## Complete Example Project Structure

```
YourGame/
├── Plugins/
│   └── StudentRAGAgent/
│       └── (Plugin files as described above)
├── Content/
│   ├── Blueprints/
│   │   ├── BP_RAGAgentManager
│   │   └── BP_StudentCharacter
│   └── UI/
│       └── WBP_StudentRAGChat
└── Config/
    └── DefaultRAGAgent.ini
```

This integration provides a complete solution for using the Student Educational RAG Agent in Unreal Engine 5 with all features enabled.

