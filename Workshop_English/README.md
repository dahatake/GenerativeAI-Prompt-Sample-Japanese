# Workshop

Depending on your current job, schoolwork, or other interests, replace each Prompt.

Prompt is text after all, so please follow the steps that are easy for you.

This section is "What do you want to do?" It is for those who are lost.

1. Start a text editor such as **Notepad**. 
1. Copy the "Prompt" text and paste it into Notepad, etc.
1. Replace the "<<xxx character >>" part of the prompt with a character such as an email.  


# Notes!!!

- When dealing with business data, please **remove** privacy (e.g., personal names) and confidential information (information that cannot be disclosed) or **replace it with another character**. For example, replace it with non-identifiable information such as {Mr. A} or {Company B}.

- If you want to change tasks, create a new Chat thread and then enter the following prompt.

# 1. basis

## 1.1. transformation

### Correction of apology email

Scenario:

I'm late for a meeting with an important customer. After it was over, I decided to send an email apologizing. Thailand would like my boss to correct my email, but my boss is away due to family urgency. Ask ChatGPT to correct this email.

Prompt:
```text
### Instructions
Please create the best possible apology formal email according to the following Text for the customer executive person.
Please list the explanation of reason of why you corrected as an improvement point.

### Text
Mr./Ms. Hatakeyama. Even though my flight was delayed the other day, I was sorry to be 15 minutes late for the meeting. I will be careful in the future.
```

Consideration:
- Let's say you're a paid field support engineer. Let's say the customer is paying 10,000 yen per hour. What to do?

### Keep your sentences plain

Scenario:

I've been accepted into a new role. There are a few products that need to be procured, but I'm not familiar with them. There is also a handover document, but the information has been updated because the target is a cloud service. I would like to understand the content of Thailand.
Modify expert sentences into plain language that anyone can understand.

Prompt:
```text
### Role
You are a kindergarten teacher. He is very good at talking to children.

### Instructions
Please put the following sentences in plain language so that even kindergarten children can understand them.

### Text
GPT-3, GPT-3.5, and GPT-4 models from OpenAI are prompt-based. With prompt-based models, the user interacts with the model by entering a text prompt, to which the model responds with a text completion. This completion is the model’s continuation of the input text.

While these models are extremely powerful, their behavior is also very sensitive to the prompt. This makes prompt construction an important skill to develop.

Prompt construction can be difficult. In practice, the prompt acts to configure the model weights to complete the desired task, but it's more of an art than a science, often requiring experience and intuition to craft a successful prompt. The goal of this article is to help get you started with this learning process. It attempts to capture general concepts and patterns that apply to all GPT models. However it's important to understand that each model behaves differently, so the learnings may not apply equally to all models.
```

source:
https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering

### Japanese Correction

Scenario:

I was able to get in touch with an engineer from a manufacturer with whom I have business dealings. Our engineers have looked it up, and we have information in English. However, rather than communicating with the manufacturer's engineers, he/she is more interested in solving other technical problems that arise. Therefore, I decided to send an email in Japanese myself. Ask ChatGPT to correct your Japanese emails.

Please follow this "Creation of Japanese sentences at the next level".

```prompt
### Instructions
Please do not change the message of the following scenario and correct it to the N1 level of the JLPT.
Please write the corrected text in Japanese. Please write the reason why you made the improvement in English.

### Scenario
使っているクラウドサービスの技術的な問題をみつけました。ストレージに問題がありそうです。ディスクIOがピークに近いと思います。これをどうやってチェックできますか？
```

- Please 😊 replace the sentence by writing your own Japanese essay

## 1.2. extraction

### Summary

Scenario:

I took a one-week vacation. I'm going back to work tomorrow, but I have a few projects that I'm interested in.
One of the biggest projects is about to start, and I have a long email with people outside the company who have been communicating with me for several weeks about it. There were several things to talk about, and there were a few things that had not been decided before the vacation. There was also likely to be a conflict of opinion. I would like to understand the situation.

It will summarize the sentence from the email and the memorandum of the meeting.

Replace the <<email body>> in the prompt with the actual email body.

Prompt:

```text
### Instructions
Please summarize the email below.

### Email
<<メール本文>>

```

### Extracting Items

Scenario:

Same as above.

```text
### Instructions
Please make a list of each {item} in the email below. If you don't understand something, please mark it as "[Unknown]".

### {item}
- Summary
- Purpose
- Scope
- Deliverable
- Schedule
- Cost
- Risk
- Quality Requirements
- Resource
- Action Plan

### Email
<< text of the email>>
```

If you don't have an email body that you can use right away, please use 😊 the text of this email as an example

```text
Daiyu Hatakeyama

Mr./Ms. Hatakeyama, thank you for your quick response.

Yes, you can bring your own PC.
We apologize for the inconvenience, but it is 30 minutes before the session. In other words, please arrive at the venue at 8:30. Our staff will guide you.

Daiyu
---------------------------------------------------------
Daiyu Hatakeyama

Thank you, Mr./Ms. Hatakeyama.
Can you tell me one thing? Thailand would like to bring a PC for presentations, is that okay? I need my own PC to do the demo.

Kind Regards,
--------------------------------------------------------
daiyu hatakeyama

Mr./Ms. Hatakeyama, thank you very much for taking the time to talk with us.
The following are the requirements. If you have any questions, please let me know.

Date: July 15, 2024
Time: 9:00-10:00
What: How to use ChatGPT to cut down on meetings
Location: Microsoft Shinagawa Office of Japan
Participants: General employees and decision-makers

Thank you.
Daiyu
Contso Corporation
```

Consideration:

- For example, "Where is the place?" Etc. Try asking about additional topics in the chat continuously.

## 1.3. Classification and quantification by example

Scenario:
Analyze your social post data. In this context, I would like to conduct a sentiment analysis of the posted Thailand. To do this, I ask you to enter a sentence and categorize and quantify your emotions in response to that sentence.

Here, in the Prompt, we will show you the format, classification, and relative numerical value (between 0-100 points, etc.) that you want to answer as an "example".
In this example, "wow" is the word or sentence you want to Thailand that you actually want to evaluate.

### Basics

Prompt:
```text
Do not print explanatory text.

It's awesome, isn't it? Mr./Ms. Hatakeyama's coolness. : Positive, 100 point
Mr./Ms. Hatakeyama, it's no good. I'm late: Negative, 5 point
Mr./Ms. Hatakeyama, wow!:
```

### Specify Output Format

Scenario:

This is similar to the previous scenario. The engineer said he wanted the data in JSON. You can create it in JSON format from Excel, but you can't install the additional application on the company PC. That's why we want ChatGPT to create data in JSON format for Thailand.

Prompt:
```text

{
    "Comment": "That's awesome, how cool Mr./Ms. Hatakeyama is",
    "Emotion": Positive,
    "Score": 100
}

{
    "Comment": "Mr./Ms. Hatakeyama, I'm not good, I'm late",
    "Emotion": Negative,
    "Score": 5
}

{
    "Comment": "Mr./Ms. Hatakeyama, wow!",
    "Emotion":
    "Score":
}
```

## 1.4. Creating a table from a sentence - an application of extraction

Scenario:

In the email, you talk about multiple items in sentences. In fact, each of them has something in common, but it is difficult to understand it just by reading the text, and I think it is Thailand to check whether you have a common understanding with the other person. So, I ask them to type in a sentence and create a table of data for me.

Prompt:
```text
### Instructions
Unstructured sentences are provided. Create data in CSV format with it

### Text
On the recently discovered planet Gooklux there is a fruit of Mr./Ms.. Neo-skizzle is purple and tastes like candy. Roheckle is a grayish-blue fruit with a lemon-like sourness. Punitz is bright green in color, more savory than sweet. There is also a Mr./Ms. loop nova that tastes like neon pink and cotton candy. Finally, there is a fruit called grohl, which has a very sour bitterness with a sour and caustic taste, and a pale orange tinge.
```

## 1.5. Create a learning plan to learn a new topic

Scenario:

There are new technologies and services that are not yet widely used in the world. I have some understanding of the technology and services, but I need to create a learning plan that will be easy for many other people to understand.
Training companies have never covered the topic before. I need to make the final decision when we make a plan together, so I would like you to draft Thailand it.

Prompt:

```text
### Role
You are an expert in educating students in LLMs at universities and other higher professional educational institutions.

### Instructions
Create a plan to learn Prompt with ChatGPT. In your plan, focus on summaries, role definitions, and Few-Shot Learning. Consider some examples of common mistakes learners make. Create specific assignments as well.
```

## 1.6. Creating a Simple Program

Scenario:

I became interested in programming during my DX training. I also bought books on programming languages, but it is difficult to study each time because new ones come out within half a year.
I was advised to read the Mr./Ms. code, but it is very difficult to search for the Mr./Ms. code. Thailand can verbalize what you want to do to some extent.
That's why we want ChatGPT to create Mr./Ms. code for Thailand.

Execute the following Prompt to create an HTML string. Copy the string to a text editor such as Notepad and save it to a location of your choice with the file name "helloworld.html". Open the file in any browser, type your name in the text box, and press the button.

Prompt:
```text
Write JavaSctipt program code that does the following:

### Web screen configuration
The following is placed on the screen of the web.
label
Text box button
button

### Code
When you click the button, combine the word "Welcome" with the text entered in the text box and display it in a message box.
```

# 2. Practice

## 2.1. Social and business surveys

Do this only if you have access to Microsoft Copilot (Bing Chat).

Microsoft Copilot:
https://copilot.microsoft.com/

Scenario:

During the meeting, the topic of "Japan people are busy" came up. However, there seemed to be no basis for this. For this reason, I would like to conduct a survey on the work of Japan employees during the meeting and summarize the results as Thailand report.
I heard that various survey information is often published on the Internet. In particular, survey reports by governments, government offices, local governments, and universities are often published on websites or in PDF formats. Therefore, we would like Thailand to create a report based on that information.

Prompt:
```text
In major countries such as Japan, please display data on what tasks and how much time employees are spending on each task. Whenever possible, create trends from the past with your data.
You should also create a sentence summarizing each piece of data.
If you have multiple years of data for one data, display the data in a tabular format.
If possible, create a graph for each of them.
```

The output may not be finished at once. In that case, please prompt "Please continue working".

If you can use **Microsoft Edge** in your web browser  , please continue with: 

- In the Microsoft Copilot output, there is a website link as the source. Click on it to go to that site. 
- Click the **Copilot icon** in the upper right corner of your browser to bring up Microsoft Edge Copilot. 
- Enter a Prompt similar to the following:

```text
Summarize this page.
```

In Microsoft Edge Copilot, if you have access to a site or PDF file displayed in the browser, load the content and execute a prompt.

Microsoft Edge Copilot:
https://www.microsoft.com/ja-jp/edge/features/copilot?form=MA13FJ

If you are interested in other research subjects, please refer to ... Sorry the all of the following is in Japanese.

Prompt:
```text
What are the major business challenges in manufacturing? Find out more about the following:

- Challenges: What specific challenges are there?
- Cause: What exactly is causing it?
- Initiatives: What are companies doing to address the issues and causes? Explanation of specific cases
- Examples of using generative AI: If there is a company or organization that uses generative AI in its initiatives, explain specific examples of its use
```

The following is not a Prompt. As part of your work, use Bing Chat or ChatGPT to do it.

Subject:
- Do some research on ChatGPT usage. We will summarize specific use cases in each country and industry. What are the advantages and disadvantages of introducing it for companies?

## 2.2. Technology Problem Solving

Scenario:

If you encounter a technical problem, such as an error in an application you're using or poor performance, ask them to investigate how to resolve the issue.

```prompt
Azure Cosmos DB query performance is poor.
List the possible possible causes, how they are measured, and the solution.
You should also create detailed instructions for solving the problem.
```

## 2.3. Simulating a meeting

Scenario:

For meetings where decisions need to be made, team members create materials that serve as a starting point for discussions. Every time. We spend a lot of time doing that. Therefore, I would like to Thailand to have a procedure drawn up for creating materials that will serve as a basis for discussion.
Also, in most cases, there are items such as "Needed Help", but it is often discussed on the premise of a single conclusion, "do" or "not do". In reality, there should be options for the business, such as "do it," "don't do it," or "do it later," but there has rarely been a discussion on each pattern.
This time, I would like ChatGPT to simulate the meeting itself and create minutes of Thailand results.

After "### condition ###", please replace it with the one you are currently discussing.
For **{Info}** , enter the following prompt in Bing Chat to gather information. 

例:
```text
Make a list of the pros and cons of companies implementing ChatGPT.
```

Note: The following is a sample is in Japanese.

[Simulate Meeting](/会議/ディスカッションをさせる.md)


```text

As for how to think, try something other than lateral thinking.

Define the direction of thought:
```
Note: The following is a sample is in Japanese.

[Direction of Thought](/高度なテクニック/README.md#3-思考の方向性を示す言葉たち)


## 2.4. Application Prototyping Development

Scenario:

There are customers who need a new application, but they are not sure whether they can expect a return on investment by developing the application, so the conversation is not moving forward.
Also, the customer says that they are not familiar with IT, so even if you ask them about their business requirements, you will not be able to get the information you have obtained. It is also possible that the person is speaking out of his or her personal taste.
So, we decided to develop a prototype Thailand and show it to Thailand to see what the business requirements were.
If possible, I would like Thailand have a prototype created within Thailand few days.

From defining business requirements to designing, developing, and deploying. We will do it all at once.
It takes 10-15 minutes (in fact, it has been halved in the last few months)

Note: The following is a sample is in Japanese.

[Proto-Typing](/Software%20Engineer/アプリのプロトタイプ開発/)

# 3. Ask ChatGPT to review

## 3.1. Review of Prompt

Scenario:

Even if you write a prompt many times, "Is it conveyed in this way?" There are many things that make me anxious. Therefore, I would like you to review the Prompt Thailand.
Of course, it would be nice if there was someone who was familiar with Prompt when reviewing it.

Here, I'll ask ChatGPT itself to review the prompt I wrote.

Prompt:
```text
What prompt should I have entered at the very beginning to resolve this issue efficiently? Create a prompt for it and a description of the improvement.
Take a deep breath and take it one step at a time.
```

