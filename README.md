# 🎨 Artify API – User Authentication (Signup & Signin)

This project provides user authentication APIs using **Django** and **Django REST Framework**, supporting user types like `artist`, `buyer`, and `admin`.

---

## 📍 Base URL

```
https://yourdomain.com/api/users/
```

---

## 🔐 Signup API

**Endpoint:**

```html
<pre>
  <code id="signup-endpoint">POST /api/users/signup/</code>
  <button onclick="navigator.clipboard.writeText(document.getElementById('signup-endpoint').innerText)">📋 Copy</button>
</pre>
```

Registers a new user.

### 📥 Request Fields

| Field           | Type   | Required | Description                                                       |
|-----------------|--------|----------|-------------------------------------------------------------------|
| `username`      | string | ✅ Yes   | Unique username                                                   |
| `email`         | string | ✅ Yes   | Valid email address                                               |
| `password`      | string | ✅ Yes   | Minimum 6 characters (write-only)                                 |
| `user_type`     | string | ❌ No    | Options: `artist`, `buyer`, or `admin` (default: `buyer`)         |
| `phone_number`  | string | ❌ No    | Optional phone number                                             |
| `profile_image` | file   | ❌ No    | Optional profile image (multipart/form-data)                      |

### 🧪 Sample JSON Request

```json
{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "securepass123",
  "user_type": "artist",
  "phone_number": "03001234567"
}
```

### ✅ Sample JSON Response

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "johndoe@example.com",
  "user_type": "artist",
  "phone_number": "03001234567",
  "profile_image": null
}
```

---

## 🔑 Signin API

**Endpoint:**

```html
<pre>
  <code id="signin-endpoint">POST /api/users/signin/</code>
  <button onclick="navigator.clipboard.writeText(document.getElementById('signin-endpoint').innerText)">📋 Copy</button>
</pre>
```

Authenticates a user using their username and password.

### 📥 Request Fields

| Field      | Type   | Required | Description                |
|------------|--------|----------|----------------------------|
| `username` | string | ✅ Yes   | Registered username        |
| `password` | string | ✅ Yes   | User password (write-only) |

### 🧪 Sample JSON Request

```json
{
  "username": "johndoe",
  "password": "securepass123"
}
```

### ✅ Sample JSON Response

```json
{
  "message": "Login successful",
  "token": "your-auth-token",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "johndoe@example.com",
    "user_type": "artist"
  }
}
```

### ❌ Error Responses

**Invalid credentials:**

```json
{
  "non_field_errors": ["Invalid username or password."]
}
```

**Disabled user:**

```json
{
  "non_field_errors": ["User account is disabled."]
}
```

---

> 💡 **Note:** The copy buttons will only work on platforms that support HTML inside Markdown like GitHub (partial support) or custom docs websites (fully supported).  
> On GitHub, you may consider using custom documentation tools (like [Docusaurus](https://docusaurus.io/), [MkDocs](https://www.mkdocs.org/), or Swagger UI) for full interactivity.



