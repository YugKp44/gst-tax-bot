## 📚 Data Sources Used
This chatbot is designed to answer questions on **Indian GST and Income Tax laws**. The knowledge base is compiled from trusted and government-authorized documents. Below is a summary of all data sources used to build the FAQ corpus.

---

### 1. 🧾 GST-Related Data
| Source                        | Description                                                              | Link                                                                         |
| :---------------------------- | :----------------------------------------------------------------------- | :--------------------------------------------------------------------------- |
| **CBIC GST Portal**           | Official government portal for all GST-related rules, returns, and FAQs. | <https://cbic-gst.gov.in>                                                    |
| **FAQ on TDS under GST**      | Detailed questions on TDS provisions under the GST Act.                  | <https://incometaxindia.gov.in/Pages/faqs.aspx>                      |
| **Advance Ruling FAQs**       | Frequently asked questions on advance tax rulings under GST.             | <https://incometaxindia.gov.in/Pages/faqs.aspx> |
| **Returns (GSTR‑1, GSTR‑3B)** | Filing instructions, timelines, and penalties.                           | CBIC Downloads Section                                                       |
<https://tutorial.gst.gov.in/>

---

### 2. 💰 Income Tax-Related Data
| Source                      | Description                                                        | Link                                                                               |
| :-------------------------- | :----------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| **Income Tax India Portal** | Official IT department portal for laws, deductions, and TDS rates. | <https://incometax.gov.in>                                                         |
| **FAQs on TDS / TCS**       | Covers key provisions under sections 194C, 194I, 206C, etc.        | <https://incometaxindia.gov.in/pages/tax-information-services.aspx> |
| **Section 80C Deductions**  | List of eligible deductions and investments.                       | <https://incometax.gov.in/>                         |
| **PAN & e-Filing FAQs**     | Common doubts on filing returns for individuals and freelancers.   | <https://incometaxindia.gov.in/pages/faqs.aspx>                     |

---

### 3. 🤖 Additional Resources
| Type                           | Description                                                                    |
| :----------------------------- | :----------------------------------------------------------------------------- |
| **Govt Notifications**         | Notifications from CBIC and CBDT used for verifying limits and latest changes. |
| **Chartered Accountant Blogs** | Used for cross-checking common-use language (with caution).                    |
| **Finance Ministry Circulars** | Used for rare or situational queries.                                          |

---

### 4. 📁 Data Format
All raw content (PDF, HTML, text) was converted into structured question-answer pairs. The JSON format used:

```json
{
  "question": "What is the due date for filing GSTR-3B?",
  "answer": "The due date is generally the 20th of the subsequent month, but can vary by turnover or state.",
  "source": "cbic-gst.gov.in"
}
```
This dataset was then embedded and indexed using FAISS for fast similarity-based retrieval.

---
### ⚠️ Notes
* All content is non-confidential and available in the public domain.
* No generative model was fine-tuned on this data — the data was used for retrieval-augmented generation (RAG).
* Sources were cited explicitly in the chatbot's context for transparency.
