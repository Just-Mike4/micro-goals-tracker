#  Micro Goals Tracker API

The Micro Goals Tracker API is a RESTful API designed to help users set, track, and manage their personal goals effectively. It provides endpoints for user authentication, goal creation, progress tracking, and analytics. Users can also set reminders and view detailed statistics about their habits and achievements.

## Features:
**User Management:** Register and log in to access personalized goal tracking.
**Goal Management:** Create, edit, delete, and view goals.
**Progress Tracking:** Mark goals as completed, view streaks, and analyze progress over time.
**Analytics:** Get insights into habits, including streaks and consistency.
**Reminders:** Set daily reminders for goals to stay on track.

## API Endpoints Documentation

## POST `/api/register/`
Create a new user account.  
**Request Body:**
```json
{
    "username": "tina",
    "email": "tina@example.com",
    "password": "strongpassword"
}
```
**Response:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "token": "d65b24fe38a0456a8c..."
}
```


## POST `/api/login/`
Get authentication token.  
**Request Body:**
```json
{
    "username": "tina",
    "password": "strongpassword"
}
```
**Response:**
```json
{
  "token": "d65b24fe38a0456a8c..."
}
```


## POST `/api/goals/`
Create a new goal.  
**Request Body:**
```json
{
    "title": "Read 5 pages",
    "description": "Build reading habit",
    "reminder_time": "20:00"
}
```
**Response:**
```json
{
    "id": 1,
    "title": "Read 5 pages",
    "description": "Build reading habit",
    "created_at": "2025-04-21T13:00:00Z",
    "reminder_time": "20:00"
}
```



## GET `/api/goals/`
List all current user’s goals.  
**Query Options:**
- `?date=2025-04-21` → See progress for a specific day.  
- `?search=read` → Search by goal title.



## GET `/api/goals/{id}/`
Get a single goal with its streak info.  
**Response:**
```json
{
    "id": 1,
    "title": "Read 5 pages",
    "streak": {
        "current": 5,
        "longest": 9
    },
    "last_checkin": "2025-04-20"
}
```



## PUT `/api/goals/{id}/`
Edit a goal.



## DELETE `/api/goals/{id}/`
Delete a goal.



## POST `/api/goals/{id}/checkin/`
Mark a goal as completed for today.  
**Request Body:**
```json
{
    "date": "2025-04-21"
}
```
**Response:**
```json
{
    "message": "Goal marked as completed for today.",
    "current_streak": 6
}
```



## GET `/api/goals/{id}/progress/`
Get progress log (e.g., for a heatmap/calendar view).  
**Response:**
```json
[
    {"date": "2025-04-16", "completed": true},
    {"date": "2025-04-17", "completed": true},
    {"date": "2025-04-18", "completed": false},
    {"date": "2025-04-19", "completed": true}
]
```



## GET `/api/analytics/`
Return general habit statistics for the current user.  
**Response:**
```json
{
    "total_goals": 3,
    "active_goals": 3,
    "completed_today": 2,
    "longest_streak_overall": 11,
    "most_consistent_goal": {
        "title": "Read 5 pages",
        "current_streak": 6
    }
}
```



## POST `/api/reminders/`
Set daily reminder preferences for a goal.  
**Request Body:**
```json
{
    "goal_id": 1,
    "reminder_time": "20:00",
    "enabled": true
}
```



## GET `/api/reminders/`
List all reminders and times.  

## PATCH `/api/reminders/{id}`
**Request Body:**
```json
{
    "reminder_time": "20:00",
    "enabled": true
}
```