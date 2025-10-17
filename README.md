# DevDen Discord Bot

A feature-rich Discord bot designed for the DevDen community, providing tools for user engagement, project management, and advanced moderation. Built using `discord.py` with modern application commands (slash commands).

---

**Installation:**

1. `git clone https://github.com/camysticc/general-discord-bot.git`
2. `bash startup.sh` or click `startup.sh`
3. Ready to go!


## 🚀 Key Features

* **Project Tracking:** Create and manage community projects with unique IDs and status updates.
* **User Profiles:** Allows members to create and share custom personal profiles.
* **Dynamic Help:** An interactive help menu with buttons for key server information.
* **Application & Feedback Flow:** Structured commands for submitting developer applications, bug reports, and feedback.
* **Advanced Moderation:** Tools for setting post permissions, creating private investigation channels, and viewing the ban list.
* **Persistent Data:** Uses JSON files for data persistence (`profiles.json`, `projects.json`, `tags.json`).

---

## ⚙️ Command List (Slash Commands)

Most staff/admin commands are restricted to users with the configured staff role you set!

### 👥 General & Utility Commands

| Command | Description | Arguments | Restrictions |
| :--- | :--- | :--- | :--- |
| **`/help`** | Displays a help menu with buttons for **Server Rules** and **Freelancing Roles**. | None | None |
| **`/whoami`** | Displays the user's Discord ID, account creation date, and server join date. | None | None (Ephemeral) |
| **`/stats`** | Displays bot statistics (servers, users, memory usage, discord.py version). | None | None |
| **`/profile`** | Allows a user to create, view, or update their personal profile. | `[user: @member]` (Optional) | None |
| **`/color`** | Previews a color based on a 6-digit hex code. | `hex_code: <#FF5733>` | None (Ephemeral) |
| **`/apply-dev`** | Initiates an application process for a developer role (uses dropdown/modal). | None | None |
| **`/feedback`** | Submits feedback and a 1-5 star rating for a developer. | None | None (Uses a modal) |
| **`/bug-report`** | Submits a structured bug report (uses dropdown/modal). | None | None |

---

### 💼 Project Management

These commands are used to track community and commission projects.

| Command | Description | Arguments | Restrictions |
| :--- | :--- | :--- | :--- |
| **`/set-project-id`** | Creates a new project, assigns a unique 6-char ID, and records the department. | `creator: @member`, `recipient: @member` | None (Intended for project initiators) |
| **`/project-status`** | Views the details and current status of a project by its ID. | `project_id: <ID>` | None (Ephemeral) |
| **`/manage-status`** | Updates the status of an existing project (e.g., "In Progress", "Completed"). | `project_id: <ID>` | Restricted to the **project creator** |

---

### 🏷️ Tag System (`/tags` Group)

A command group for managing persistent, reusable server tags.

| Subcommand | Description | Arguments | Restrictions |
| :--- | :--- | :--- | :--- |
| **`/tags view`** | Displays the content of a saved tag. | `name: <tag name>` | General Use |
| **`/tags list`** | Shows a list of all existing tag names. | None | General Use (Ephemeral) |
| **`/tags create`** | Creates and saves a new tag. | `name: <name>`, `content: <content>` | Staff Role Only |
| **`/tags edit`** | Modifies the content of an existing tag. | `name: <name>`, `new_content: <content>` | Staff Role Only |
| **`/tags delete`** | Permanently removes a tag. | `name: <name>` | Staff Role Only |

---

### 🛡️ Moderation & Staff Commands

These features are restricted to staff roles for server management.

| Command | Description | Arguments | Restrictions |
| :--- | :--- | :--- | :--- |
| **`/set-nickname`** | Changes the nickname of a target user. | `user: @member`, `nickname: <new name>` | Staff Role Only |
| **`/lock`** | Prevents the `@everyone` role from sending messages in the specified channel. | `channel: #channel` | Staff Role Only |
| **`/flag`** | Creates a **private investigation channel** for a specified user. | `user: @member` | Staff Role Only |
| **`/post-ban`** | Prevents a user from sending messages in a list of pre-configured channels. | `user: @member`, `reason: <reason>` | Staff Role Only |
| **`/un-post-ban`**| Reverses the post-ban, allowing the user to post again. | `user: @member`, `reason: <reason>` | Staff Role Only |
| **`/ban-list`** | Displays a list of all currently banned users on the server. | None | Staff Role Only (Ephemeral) |
| **`/dev-of-the-month`**| Sends a public announcement recognizing a developer. | `member: @member` | **Administrator** Only |
