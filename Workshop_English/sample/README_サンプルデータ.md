対応Prompt: [..\README.md](..\README.md)

> このファイルの内容はすべて研修用の架空データです。説明は日本語ですが、貼り付け用の source data は英語中心で作成しています。

# Shared fictional scenario

- Company: Hokushin Factory Solutions
- Product: `LunaPlant`, an industrial monitoring and field-service platform
- Your role: Customer success and rollout lead
- Goal: Prepare for the `Factory Copilot Kickoff` customer workshop in October 2026

## 1. Apology email correction

```text
Customer:
- Ms. Eleanor Price, Operations Director, Northwind Components

What happened:
- You arrived 17 minutes late to a paid on-site workshop because your connecting train was suspended by severe weather.
- The workshop still happened, but the Q&A session was shortened.

Rough draft to fix:
Dear Eleanor,
I am sorry I was late today. The train stopped because of weather and I got there late. I will be careful next time. Thank you for waiting and I hope the demo was okay.

Facts to preserve:
- The weather issue is factual.
- You are not asking for forgiveness directly.
- The follow-up meeting time is not confirmed yet.
```

## 2. Keep your sentences plain

```text
Audience:
- Eight new sales hires
- Two warehouse supervisors with limited IT background

Original text:
Our retrieval-augmented generation workflow vectorizes case notes, workshop recordings, and proposal documents every night, stores them in a permission-aware index, and reranks candidate passages at query time so that answer grounding remains aligned with both security boundaries and business metadata.

Output constraints:
- Explain it in very plain English
- Keep the ideas of "where the data comes from", "how the search works", and "why it is safe"
- Avoid jargon unless you explain it immediately
```

## 3. Japanese correction

```text
Situation in English:
- You need to email a Japanese cloud vendor engineer.
- Your team observed a possible storage I/O bottleneck.
- You want polite business Japanese without changing the meaning.

Draft in Japanese:
ストレージの遅さを見つけました。9時10分から9時25分までディスクキューが高かったです。バックアップのせいかアプリのせいかまだ分かりません。確認のためにどのログを見るべきか教えてください。
```

## 4. Summary / extracting items

```text
Subject: Re: Workshop logistics for the Factory Copilot Kickoff

From: Maya Collins
To: Rollout Team, Legal, Marketing
Date: 2026-09-02 08:15

The customer has increased the attendance from 9 people to 14. Eight will join on site and six remotely. They also asked whether we can provide a short security overview before the live demo.

From: Jordan Lee
Date: 2026-09-02 09:02

We can add the security overview, but the current deck only has one slide and it does not mention tenant isolation. We should update it before September 25. Also, the FAQ summarization demo still has only 82 validated sample records.

From: Priya Shah
Date: 2026-09-02 10:41

Legal approved the use of the BlueRiver case study if we remove the customer division name and replace the exact savings amount with a percentage range.

From: Maya Collins
Date: 2026-09-02 13:05

One more note: the venue team allows only six guest laptops because of the power layout. Please keep the printed handout under six pages.
```

### Item extraction hints

- Purpose
- Scope
- Deliverable
- Schedule
- Cost
- Risk
- Resource
- Action Plan

### Known gaps

- No owner is assigned for the security slide update
- The source of the missing 18 demo records is unclear
- The final handout deadline is not stated explicitly

## 5. Classification and quantification by example

```text
Comments to classify:
1. The demo was clear and practical. I want my team to try it next week.
2. Helpful session, but I still do not see how this fits our approval workflow.
3. Another tool? This sounds like extra overhead for the plant managers.
4. The FAQ summary feature looks promising, especially for weekly escalations.

Desired JSON fields:
- Comment
- Emotion
- Score
- Confidence

Rules:
- Emotion values: Positive / Neutral / Negative / Mixed
- Score range: 0-100
- Confidence range: 0.00-1.00
```

## 6. Creating a table from a sentence

```text
Unstructured paragraph:
Hokushin offers four rollout packages. QuickStart lasts two weeks and costs 45,000 JPY-equivalent units for first-time customers. Standard Launch lasts six weeks, costs 120,000, and is intended for multi-site deployments. Premium Success runs for three months at 260,000 and includes monthly reviews plus training. Rescue Plan has a 30,000 setup fee, no fixed duration, and extra charges depending on the number of on-site visits.

Columns you want in CSV:
- Package
- Duration
- Price
- Target customer
- Included services
- Unknowns
```

## 7. Learning plan for a new topic

```text
Topic:
- Learning prompt design for business reporting with ChatGPT and Microsoft 365 Copilot

Learners:
- 12 business users with no coding background
- 90 minutes per session, 4 weeks

Include:
- Summaries
- Role prompting
- Few-shot examples
- Common mistakes
- Homework assignments
```

## 8. Creating a simple program

```text
Program request:
- Build a single HTML file with a text box and a button.
- When the user enters a visitor name and clicks the button, show "Welcome, <name>" in an alert box.

Extra constraints:
- Light blue background
- Centered layout
- No external libraries
- Mobile-friendly spacing
```

## 9. Social/business survey and follow-up page summary

```text
Research brief:
- Compare how office workers in Japan, Germany, and the United States spend time on meetings, email, document creation, and analysis work.
- Prefer official or academic sources.
- Show multi-year trends when available.
- Call out differences between manufacturing and information-services sectors if possible.

Fictional training sources:
- Aoba Institute for Labour Policy, "2026 Japan-Germany-US Office Work Time Survey"
  - URL: https://research.aoba.example/en/reports/2026-office-work-time
- International Digital Work Productivity Forum, "Cross-country Digital Work Survey 2026"
  - URL: https://idwp.example/publications/digital-work-survey-2026
- Future Manufacturing Industry Association, "Indirect Work Productivity White Paper 2026"
  - URL: https://fmia.example/whitepapers/indirect-work-2026

Selected mock page text:
Title: 2026 Japan-Germany-US Office Work Time Survey
Publisher: Aoba Institute for Labour Policy
Published: August 18, 2026
Fieldwork: April 1-May 31, 2026
Population: Full-time employees at manufacturing and information-services companies with at least 300 employees
Valid sample: 2,400 respondents—800 each in Japan, Germany, and the United States; each country sample contains 400 manufacturing and 400 information-services employees
Method: A ten-business-day work diary combined with an online questionnaire. Results are average minutes per employee per workday.

Key findings:
- Meeting time: Japan 96 minutes, Germany 71 minutes, United States 84 minutes.
- Email and chat: Japan 78 minutes, Germany 54 minutes, United States 69 minutes.
- Document creation: Japan 64 minutes, Germany 51 minutes, United States 58 minutes.
- Analysis and decision work: Japan 49 minutes, Germany 67 minutes, United States 73 minutes.
- In Japanese manufacturing, meetings plus internal approvals take 132 minutes, compared with 104 minutes in information services.
- Compared with the 2022 edition, meeting time in Japan fell by 8 minutes while email and chat time rose by 11 minutes.

Limitations:
- The diary includes self-reported entries and may differ from instrumented measurements.
- Management-level representation differs by country.
- Internal approval processes are not defined identically across participating companies.
```

### Edge follow-up prompt

```text
Summarize the mock page text above. Extract the survey population, survey year, sample size, and numbers related to meeting time or administrative work. Separate findings from study limitations.
```

### Manufacturing challenge research prompt support data

```text
Industry focus:
- Mid-sized manufacturers adopting AI for proposal writing, support operations, and maintenance reporting

What to capture:
- Specific pain points
- Root causes
- Real-world initiatives
- Generative AI examples
```

## 10. Technology problem solving

```text
Problem statement:
- Azure Cosmos DB query latency increased from 180 ms to 920 ms during the last two weeks.
- The slowdown is visible in read-heavy dashboards between 08:30 and 11:00 JST.
- RU consumption is flat, but p95 latency and throttling spikes are both being reported.
- A new composite index was deployed on 2026-08-20, and a data import job was added on 2026-08-24.

What is still unknown:
- Whether the import job overlaps with dashboard traffic
- Whether the new query shape is using the intended index
- Whether cross-partition fan-out has increased
```

## 11. Prompt review

```text
Prompt to review:
Please summarize the meeting, write a customer email if needed, mention risks, and make it sound good. Keep it short unless more detail is useful.

Observed issues:
- The output format changes every time
- Customer-facing language and internal notes get mixed together
- Unconfirmed facts are sometimes written as decisions
```
