# Frontend Technical Spec

## Pages

### Dashboard `/dashboard`

#### Purpose

The purpose of this page is to provide a **summary of learning progress** and act as the **default landing page** when a user visits the web app.

#### Components

- **Last Study Session**
  - Displays the last activity used
  - Shows the timestamp of the last activity
  - Summarizes **correct vs. incorrect answers** from the last activity
  - Includes a **link to the study group**
- **Study Progress**
  - Total words studied, e.g., `3/124`
    - Shows the total words studied **across all study sessions** relative to the available words in the database
  - Displays **mastery progress**, e.g., `0%`
- **Quick Stats**
  - **Success rate**, e.g., `80%`
  - **Total study sessions**, e.g., `4`
  - **Total active groups**, e.g., `3`
  - **Study streak**, e.g., `4 days`
- **Start Studying Button**
  - Redirects to the **study activities page**

#### Needed API Endpoints

- `GET /api/dashboard/last_study_session`
- `GET /api/dashboard/study_progress`
- `GET /api/dashboard/quick_stats`

---

### Study Activities Index `/study_activities`

#### Purpose

This page displays a **collection of study activities** with thumbnails and names, allowing users to either **launch** or **review** past study sessions.

#### Components

- **Study Activity Card**
  - Displays a **thumbnail** of the study activity
  - Shows the **name** of the study activity
  - Includes a **launch button** to start the activity
  - Provides a **view button** for reviewing past study sessions

#### Needed API Endpoints

- `GET /api/study_activities`

---

### Study Activity Show `/study_activities/:id`

#### Purpose

This page displays **detailed information** about a study activity and its past study sessions.

#### Components

- Name of study activity
- Thumbnail of study activity
- Description of study activity
- **Launch button**
- **Study Sessions List (Paginated)**
  - ID
  - Activity name
  - Group name
  - Start time
  - End time _(determined by the last word review submitted)_
  - Number of review items

#### Needed API Endpoints

- `GET /api/study_activities/:id`
- `GET /api/study_activities/:id/study_sessions`

---

### Study Activities Launch `/study_activities/:id/launch`

#### Purpose

This page is responsible for **starting a new study session**.

#### Components

- **Study Activity Name**
- **Launch Form**
  - Select field for choosing a **group**
  - **"Launch Now" button**

#### Behavior

- After submission, a **new tab opens** with the study activity based on the URL stored in the database.
- The page redirects to the **study session show page**.

#### Needed API Endpoints

- `POST /api/study_activities`

---

### Words Index `/words`

#### Purpose

This page displays **all words in the database**.

#### Components

- **Paginated Word List**
  - **Columns:**
    - **Latin Word** (instead of Japanese)
    - **Pronunciation (e.g., Phonetic Transcription)**
    - **English Meaning**
    - **Correct Count**
    - **Wrong Count**
  - Pagination: **100 items per page**
  - Clicking on a word **navigates to the Word Show page**

#### Needed API Endpoints

- `GET /api/words`

---

### Word Show `/words/:id`

#### Purpose

This page displays **detailed information** about a specific word.

#### Components

- **Latin Word**
- **Pronunciation**
- **English Meaning**
- **Study Statistics**
  - **Correct Count**
  - **Wrong Count**
- **Word Groups**
  - Displayed as **tag-like pills**
  - Clicking on a **group name** navigates to the **Group Show page**

#### Needed API Endpoints

- `GET /api/words/:id`

---

### Word Groups Index `/groups`

#### Purpose

This page displays a **list of word groups** in the database.

#### Components

- **Paginated Group List**
  - **Columns:**
    - **Group Name**
    - **Word Count**
  - Clicking on a **group name** navigates to the **Group Show page**

#### Needed API Endpoints

- `GET /api/groups`

---

### Group Show `/groups/:id`

#### Purpose

This page displays **detailed information** about a specific word group.

#### Components

- **Group Name**
- **Group Statistics**
  - **Total Word Count**
- **Words in Group** (Paginated list)
  - Uses the **same component as the Words Index page**
- **Study Sessions** (Paginated list)
  - Uses the **same component as the Study Sessions Index page**

#### Needed API Endpoints

- `GET /api/groups/:id` _(name & group stats)_
- `GET /api/groups/:id/words`
- `GET /api/groups/:id/study_sessions`

---

## Study Sessions Index `/study_sessions`

#### Purpose

This page displays a **list of study sessions** in the database.

#### Components

- **Paginated Study Session List**
  - **Columns:**
    - ID
    - Activity Name
    - Group Name
    - Start Time
    - End Time
    - Number of Review Items
  - Clicking on a **study session ID** navigates to the **Study Session Show page**

#### Needed API Endpoints

- `GET /api/study_sessions`

---

### Study Session Show `/study_sessions/:id`

#### Purpose

This page displays **detailed information** about a specific study session.

#### Components

- **Study Session Details**
  - Activity Name
  - Group Name
  - Start Time
  - End Time
  - Number of Review Items
- **Reviewed Words** (Paginated list)
  - Uses the **same component as the Words Index page**

#### Needed API Endpoints

- `GET /api/study_sessions/:id`
- `GET /api/study_sessions/:id/words`

---

### Settings Page `/settings`

#### Purpose

This page allows users to **configure study settings**.

#### Components

- **Theme Selection** _(Light, Dark, System Default)_
- **Reset History Button**
  - Deletes **all study sessions** and **word review items**
- **Full Reset Button**
  - **Drops all tables** and **recreates them with seed data**

#### Needed API Endpoints

- `POST /api/reset_history`
- `POST /api/full_reset`

---
