# KEDB-AI

## AI-Powered Known Error Database for Intelligent Incident Management

KEDB-AI is a web-based Known Error Database designed to help teams document, manage, search, and resolve recurring technical incidents efficiently.

The application combines a RESTful backend, web-based frontend, authentication, structured incident management, semantic similarity, and AI-powered assistance to provide a centralized platform for handling known technical issues.

---

## 🚀 Key Features

### 🔐 Authentication
- User registration and login
- JWT-based authentication
- Protected API endpoints

### 🗃️ Known Error Management
- Create known errors
- View detailed error information
- Edit existing errors
- Delete known errors
- Track incident status
- Store symptoms, root cause, workaround, and resolution

### 🏷️ Category Management
- Create and manage categories
- Assign categories to known errors
- Filter incidents by category

### 🔎 Search & Filtering
- Search known errors by title and application
- Filter by application
- Filter by category
- Filter by status

### 🤖 AI-Powered Assistance
Users can describe a technical issue and receive assistance based on relevant known errors stored in the database.

The system displays:
- Most relevant known error
- Similarity/match score
- Category
- Current status
- Root cause
- Recommended workaround
- AI-generated recommendation

### 🧠 Semantic Similarity & Duplicate Detection
KEDB-AI uses text embeddings and cosine similarity to identify incidents that are semantically similar, even when they use different wording.

For example:

```text
"Login failed"
        ↓
   Semantic Similarity
        ↓
"Unable to sign in"
