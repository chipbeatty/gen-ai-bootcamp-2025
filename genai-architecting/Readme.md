# AI Infrastructure Plan

## Functional Requirements

The company wants to invest in **owning its infrastructure** due to concerns about:

- **User data privacy**
- **Rising costs** of managed GenAI services

They plan to invest in an **AI PC** with a budget of **$10,000–$15,000**.

The company serves **300 active students**, all of whom are located within **Nagasaki**.

## Assumptions

- The selected **open-source LLMs** should be **powerful enough** to run on hardware within the **$10,000–$15,000** budget.
- A **single server** in the office, connected to the internet, should provide **sufficient bandwidth** to serve **300 students**.
  - ⚠️ _Consider testing network capacity to confirm this assumption._

## Data Strategy

- Due to concerns about **copyrighted materials**, all training and reference materials must be:
  - **Purchased legally**
  - **Stored securely** in a **database** for authorized access
- 📌 _Consider implementing a **data governance policy** to ensure compliance with copyright laws._

## Considerations

- The company is considering **IBM Granite** because:
  - ✅ It is a **truly open-source model**
  - ✅ It has **traceable training data**, helping to avoid copyright risks
  - ✅ It provides **greater transparency** in AI decision-making
- 📌 IBM Granite model repository: [IBM Granite on Hugging Face](https://huggingface.co/ibm-granite)
- 🔍 _Explore additional open-source models with clear licensing, such as:_
  - [Meta LLaMA](https://huggingface.co/meta-llama)
  - [Mistral](https://huggingface.co/mistralai)
- 🖥️ _Assess the AI PC’s **hardware requirements** (GPU, RAM, storage) to ensure optimal performance._
- 🌐 _Evaluate potential **scaling needs** if the number of students increases._

---

### Next Steps

✅ Finalize AI PC hardware specifications  
✅ Confirm bandwidth requirements  
✅ Select and validate the open-source LLM

---
