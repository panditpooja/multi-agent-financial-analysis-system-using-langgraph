# Database Quick Reference - This Project

## 🎯 TL;DR (Too Long; Didn't Read)

**Why database?** Django needs it for sessions and system tables.

**What's stored?** Mainly your `thread_id` (for conversation continuity).

**Do I need to do anything?** Yes - run `python manage.py migrate` once.

---

## 📋 What's in the Database?

### ✅ Currently Stored

```
db.sqlite3
├── django_session
│   └── thread_id: "abc-123-def-456"  ← YOUR CONVERSATION ID
│
├── django_migrations  ← Django's migration history
├── django_content_type  ← Django's internal tracking
└── (other Django system tables)
```

### ❌ NOT Stored (But Could Be)

- Query text
- Responses
- Query history
- User accounts
- Metrics data

---

## 🔄 How It Works

```
1. User visits website
   ↓
2. Django creates session → Saves to database
   ↓
3. thread_id stored in database
   ↓
4. User asks question
   ↓
5. Django retrieves thread_id from database
   ↓
6. Processes query (no database needed)
   ↓
7. Returns response (not saved)
   ↓
8. Session persists (thread_id still in database)
```

---

## ⚡ Quick Commands

```bash
# 1. Create database (do this once)
python manage.py migrate

# 2. Start server
python manage.py runserver

# That's it! Database is ready.
```

---

## 💡 Why Sessions Need Database

**Without database:**
- ❌ `thread_id` lost on page refresh
- ❌ Can't maintain conversation context
- ❌ Each request is "new" (no memory)

**With database:**
- ✅ `thread_id` persists
- ✅ Conversation context maintained
- ✅ User can have ongoing conversations

---

## 🎓 Key Point

**The database is mainly for session storage, not for storing your queries/responses.**

Think of it like this:
- **Database = Memory** (remembers who you are via `thread_id`)
- **Not Database = Processing** (queries are processed in real-time, not saved)

---

## 📊 Database Size

**Typical size:** < 1 MB (very small!)

**What takes space:**
- Session data (your `thread_id` values)
- Django system tables (tiny)

**What doesn't take space:**
- Queries (not saved)
- Responses (not saved)
- Metrics (in-memory only)

---

## ✅ Summary

| Question | Answer |
|----------|--------|
| **Why database?** | Django needs it for sessions |
| **What's stored?** | `thread_id` and Django system data |
| **Do I need it?** | Yes, required by Django |
| **Can I avoid it?** | No, but you can minimize usage |
| **Is it big?** | No, very small (< 1 MB) |
| **Do I manage it?** | No, Django handles it automatically |

**Bottom line:** Run `migrate` once, then forget about it! Django handles the rest. 🚀

