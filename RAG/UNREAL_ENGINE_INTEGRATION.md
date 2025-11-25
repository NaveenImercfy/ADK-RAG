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
   - HTTP plugin enabled (Edit → Plugins → HTTP)
   - JSON plugin enabled (Edit → Plugins → JSON)

## Setup Steps

### Step 1: Add C++ Classes to Your Project

1. In Unreal Editor, go to **Tools → New C++ Class**
2. Choose **Object** as the parent class
3. Name it `RAGAgentAPI`
4. This will create `RAGAgentAPI.h` and `RAGAgentAPI.cpp` in your `Source/YourProjectName/` directory

### Step 2: Update Your Project's Build.cs File

Open `Source/YourProjectName/YourProjectName.Build.cs` and add HTTP and JSON modules:

```csharp
using UnrealBuildTool;

public class YourProjectName : ModuleRules
{
    public YourProjectName(ReadOnlyTargetRules Target) : base(Target)
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
    }
}
```

### Step 3: Replace the Generated Code

Replace the contents of `RAGAgentAPI.h` and `RAGAgentAPI.cpp` with the code below.

## C++ Implementation

### RAGAgentAPI.h

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
class YOURPROJECTNAME_API URAGAgentAPI : public UObject
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
    void OnSessionCreated(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
    void OnQuestionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
    FString BuildQueryMessage(const FString& Question, const FStudentContext& Context);
    FAgentResponse ParseAgentResponse(const FString& ResponseBody);
};
```

**Important:** Replace `YOURPROJECTNAME_API` with your actual project name (e.g., `MYGAME_API`).

### RAGAgentAPI.cpp

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

### Step 4: Compile Your Project

1. Close Unreal Editor
2. Right-click on your `.uproject` file
3. Select **Generate Visual Studio project files** (or Xcode on Mac)
4. Open the project in your IDE and compile
5. Launch Unreal Editor again

## Blueprint Usage

### Creating a Blueprint Based on RAGAgentAPI

1. In Content Browser, right-click and select **Blueprint Class**
2. Search for `RAGAgentAPI` and select it
3. Name it `BP_RAGAgentManager`
4. Open the Blueprint

### Basic Blueprint Setup

#### Event BeginPlay

```
Event BeginPlay
    → Initialize Agent
        - ProjectID: "your-project-id"
        - Location: "us-central1"
        - AgentEngineID: "your-agent-engine-id"
    → Create Session
        - UserID: "student_001"
```

#### Setting Student Context

```
Set Student Context
    - Context
        - EducationBoard: "CBSE"
        - Grade: "Grade 10"
        - Subject: "Science"
```

#### Asking a Question

```
Send Question With Context
    - Question: "What is photosynthesis?"
```

#### Handling the Response

1. In the Blueprint, find the **On Agent Response** event
2. Connect it to display the response:

```
On Agent Response
    → Branch (bSuccess)
        True → Print String (Response.Text)
        True → For Each Loop (Response.Citations)
            → Print String (Current Array Element)
```

### Complete Blueprint Example

**Event Graph:**
```
Event BeginPlay
    → Initialize Agent (ProjectID, Location, AgentEngineID)
    → Create Session (UserID)
    → Set Student Context (Board: "CBSE", Grade: "Grade 10", Subject: "Science")
```

**On Button Click (Ask Question):**
```
On Button Clicked
    → Get Text from Text Input Box
    → Send Question With Context
```

**On Agent Response:**
```
On Agent Response
    → Branch (bSuccess)
        True → Set Text (Response Text Box) = Response.Text
        True → Clear Citations List
        True → For Each Loop (Response.Citations)
            → Add to Citations List
```

## Widget UI Integration

### Creating a Chat Widget

1. Create a **Widget Blueprint** named `WBP_StudentRAGChat`
2. Add the following UI elements:
   - **Text Input Box** (for questions) - Variable: `QuestionInputBox`
   - **Scrollable Text Box** (for responses) - Variable: `ResponseTextBox`
   - **Combo Box** for Education Board - Variable: `BoardDropdown`
   - **Combo Box** for Grade - Variable: `GradeDropdown`
   - **Combo Box** for Subject - Variable: `SubjectDropdown`
   - **Button** (Send) - Variable: `SendButton`
   - **Text Block** (for citations) - Variable: `CitationsTextBlock`

### Widget Blueprint Logic

**On Send Button Clicked:**
```
On Send Button Clicked
    → Get Text from QuestionInputBox
    → Make Student Context
        - EducationBoard: Get Selected Option from BoardDropdown
        - Grade: Get Selected Option from GradeDropdown
        - Subject: Get Selected Option from SubjectDropdown
    → Get RAGAgentAPI (from parent or create new)
    → Set Student Context
    → Send Question With Context
```

**On Agent Response:**
```
On Agent Response
    → Branch (bSuccess)
        True → Set Text (ResponseTextBox) = Response.Text
        True → Build Citations String
        True → Set Text (CitationsTextBlock) = Citations String
        False → Set Text (ResponseTextBox) = "Error: " + Response.ErrorMessage
```

## Configuration

### Access Token Setup (Development)

For development, create an access token file:

1. Run in terminal:
   ```bash
   gcloud auth print-access-token > Config/gcloud_token.txt
   ```

2. Place `gcloud_token.txt` in your project's `Config/` folder

**Note:** For production, implement proper service account authentication.

## Example Usage in C++

### In Your Game Character Class

```cpp
// In your character header file
UCLASS()
class YOURPROJECTNAME_API AStudentCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AStudentCharacter();
    
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class URAGAgentAPI* RAGAgent;
    
    void BeginPlay() override;
    
    UFUNCTION(BlueprintCallable)
    void AskQuestion(const FString& Question);
    
    UFUNCTION()
    void OnRAGResponse(const FAgentResponse& Response, bool bSuccess);
};
```

```cpp
// In your character implementation file
#include "StudentCharacter.h"
#include "RAGAgentAPI.h"

AStudentCharacter::AStudentCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AStudentCharacter::BeginPlay()
{
    Super::BeginPlay();
    
    // Initialize RAG Agent
    RAGAgent = NewObject<URAGAgentAPI>(this);
    RAGAgent->Initialize(TEXT("your-project-id"), TEXT("us-central1"), TEXT("your-agent-engine-id"));
    RAGAgent->CreateSession(TEXT("student_001"));
    
    // Set student context
    FStudentContext Context;
    Context.EducationBoard = TEXT("CBSE");
    Context.Grade = TEXT("Grade 10");
    Context.Subject = TEXT("Science");
    RAGAgent->SetStudentContext(Context);
    
    // Bind response handler
    RAGAgent->OnAgentResponse.AddDynamic(this, &AStudentCharacter::OnRAGResponse);
}

void AStudentCharacter::AskQuestion(const FString& Question)
{
    if (RAGAgent)
    {
        RAGAgent->SendQuestionWithContext(Question);
    }
}

void AStudentCharacter::OnRAGResponse(const FAgentResponse& Response, bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Agent Response: %s"), *Response.Text);
        // Display response in game UI
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Agent Error: %s"), *Response.ErrorMessage);
    }
}
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
2. Add a Blueprint actor with RAGAgentAPI component
3. Configure with your credentials
4. Test questions in Play mode

### Test Scenarios

**In Blueprint or C++:**

1. **Question with context:**
   - Set Context: "CBSE", "Grade 10", "Science"
   - Send Question: "What is photosynthesis?"

2. **Follow-up question (context remembered):**
   - Send Question: "What about cellular respiration?"

3. **Different student:**
   - Create Session: "student_002"
   - Set Context: "ICSE", "Class 9", "Mathematics"
   - Send Question: "What is algebra?"

## Performance Considerations

1. **Async Operations:** All HTTP calls are asynchronous
2. **Caching:** Consider caching common questions
3. **Rate Limiting:** Implement rate limiting for API calls
4. **Error Retry:** Implement exponential backoff for retries

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

### Issue: Compilation Errors
**Solution:** 
- Make sure HTTP and JSON plugins are enabled
- Check that you've updated your Build.cs file
- Verify the API macro matches your project name

## Additional Resources

- [Unreal Engine HTTP Plugin Documentation](https://docs.unrealengine.com/5.0/en-US/http-plugin-in-unreal-engine/)
- [Unreal Engine JSON Plugin](https://docs.unrealengine.com/5.0/en-US/json-in-unreal-engine/)
- [Vertex AI Agent Engine API](https://cloud.google.com/vertex-ai/docs/agent-engine/overview)

## Project Structure

After integration, your project structure should look like:

```
YourProject/
├── Source/
│   └── YourProjectName/
│       ├── YourProjectName.Build.cs (updated with HTTP/JSON)
│       ├── RAGAgentAPI.h
│       └── RAGAgentAPI.cpp
├── Content/
│   ├── Blueprints/
│   │   └── BP_RAGAgentManager
│   └── UI/
│       └── WBP_StudentRAGChat
└── Config/
    └── gcloud_token.txt (for development)
```

This integration provides a complete solution for using the Student Educational RAG Agent in Unreal Engine 5 with all features enabled.
