# Simkart Project

The Simkart project is a Django-based e-commerce platform designed for selling SimCards, offering a robust set of features including user authentication, shopping cart management, wishlist functionality, and a wallet system supporting payments in Toman (Iranian currency) and TRX (Tron cryptocurrency). Built with Django and Django REST Framework, it leverages Redis for caching and session management, ZarinPal for Toman payments, and Tron for TRX transactions. The project is intended to run within a virtual environment and includes real-time logging for errors and operations, making it suitable for both development and production environments.

## Project Overview

Simkart provides a comprehensive solution for SimCard sales, enabling users to browse, search, and purchase SimCards, add them to a cart or wishlist, and pay using a wallet system. Key features include:

- **User Interaction**: Browse SimCards, search by title or tags, leave comments, and contact support via a form.
- **Payment Options**: Pay with Toman (via ZarinPal) or TRX (via Tron blockchain).
- **Admin Capabilities**: Create, edit, and delete SimCard listings, moderate user comments, and manage contact form submissions.
- **Security**: Two-factor authentication via email verification and encrypted private keys for TRX wallets.
- **Social Sharing**: Share SimCards on WhatsApp, Facebook, and Twitter.

The project is structured into four main applications: simkart, cart, wishlist, and wallet, each handling specific aspects of the e-commerce workflow. Real-time logging ensures that errors and search activities are tracked for debugging and monitoring purposes.

## Applications

The project is organized into four Django applications, each with distinct responsibilities:

### 1. simkart

- **Purpose**: Serves as the core application, managing SimCards, user accounts, comments, and contact forms.
- **Features**:
  - Users can browse SimCards, search using titles or tags, view detailed information, and share listings on social media.
  - Supports user comments on SimCards and a contact form for support inquiries.
  - Implements two-factor authentication with email verification for registration and login.
  - Administrators can create, update, and delete SimCard listings, as well as moderate comments.
- **Key Files**:
  - `models.py`: Defines models for SimCard, Comment, Account, and ContactModel.
  - `views.py`: Provides API endpoints for listing, creating, and detailing SimCards, managing comments, and handling contact forms.
  - `serializers.py`: Serializers for API data serialization and validation.
  - `signals.py`: Automatically creates an Account for new users.
  - `permissions.py`: Custom permission class (`IsAdminOrReadOnly`) restricting write access to superusers.

### 2. cart

- **Purpose**: Manages the shopping cart, allowing users to add, remove, and purchase SimCards, as well as store shipping addresses and generate invoices.
- **Features**:
  - Users can add SimCards to their cart, adjust quantities, and remove items.
  - Supports payment integration with the wallet application for Toman and TRX transactions.
  - Stores user shipping addresses and generates invoices for completed orders.
  - Sends email notifications when items are added to the cart.
- **Key Files**:
  - `models.py`: Defines models for Cart, CartItem, Address, and Invoice.
  - `views.py`: API endpoints for cart management, item addition/removal, order completion, and invoice creation.
  - `signals.py`: Automatically creates carts for new users and invoices for completed orders.
  - `serializers.py`: Serializers for cart-related data.

### 3. wishlist

- **Purpose**: Enables users to save SimCards to a wishlist for future reference or purchase.
- **Features**:
  - Users can add or remove SimCards from their wishlist, with uniqueness enforced to prevent duplicates.
  - Automatically creates a wishlist for new users.
  - Provides a simple API for managing wishlist items.
- **Key Files**:
  - `models.py`: Defines the Wishlist model with user and SimCard relationships.
  - `views.py`: ViewSet for CRUD operations on wishlists.
  - `signals.py`: Creates a wishlist for new users.
  - `serializers.py`: Serializer for wishlist data.
  - `permissions.py`: Custom permission class (`IsAdminOrOwner`) restricting access to owners or admins.

### 4. wallet

- **Purpose**: Manages user wallets, supporting deposits and payments in Toman (via ZarinPal) and TRX (via Tron blockchain).
- **Features**:
  - Allows deposits in Toman through ZarinPal’s sandbox environment and TRX via Tron’s Shasta testnet.
  - Supports payments for shopping carts using wallet balances or direct payments.
  - Encrypts TRX private keys using Fernet for security.
  - Sends email notifications for completed transactions.
- **Key Files**:
  - `models.py`: Defines Wallet and Transaction models.
  - `views.py`: API endpoints for depositing funds, verifying transactions, and processing cart payments.
  - `zarinpal.py`: Utility class for interacting with ZarinPal’s payment gateway.
  - `signals.py`: Creates wallets for new users and sends transaction notifications.
- **Note**: This application is designed for testing purposes, using sandbox environments for ZarinPal and Tron. For production, replace sandbox credentials with valid ones.

## Installation

The Simkart project must be run within a virtual environment to isolate dependencies and avoid conflicts with system-wide packages. Follow these steps to set up the project:

1. **Prerequisites**:

   - Ensure you have Python 3.8+ and Git installed.
   - Install Redis for caching and session management (default port: 6379).

2. **Clone the Repository**:

   ```bash
   git clone https://your-repo-url.com/simkart_project_f.git
   cd simkart_project_f
   ```

3. **Create a Virtual Environment**:

   ```bash
   python -m venv myenv
   ```

4. **Activate the Virtual Environment**:

   - On Windows:

     ```bash
     myenv\Scripts\activate
     ```

   - On Linux/Mac:

     ```bash
     source myenv/bin/activate
     ```

5. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

6. **Apply Database Migrations**:

   ```bash
   python manage.py migrate
   ```

7. **Create a Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

## Configuration

Proper configuration is essential for the project to function correctly. The following steps outline the necessary setup:

1. **Set Up the** `.env` **File**: Create a `.env` file in the project root directory and populate it with the required environment variables. Replace placeholders (e.g., `...`) with actual values:

   ```
   DJANGO_SECRET_KEY=your_secure_random_key
   DJANGO_DEBUG=True  # Set to False in production
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_app_password
   EMAIL_USE_TLS=True

   REDIS_LOCATION=redis://127.0.0.1:6379/0

   JWT_ACCESS_LIFETIME_MINUTES=5
   JWT_REFRESH_LIFETIME_DAYS=1

   SUPPORT_EMAIL=support@example.com

   ZARINPAL_MERCHANT_ID=your_zarinpal_merchant_id
   ENCRYPTION_KEY=your_fernet_encryption_key
   ```

   - **Generate** `DJANGO_SECRET_KEY`: Create a secure key using Python:

     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(50))"
     ```

     Copy the output to `DJANGO_SECRET_KEY`.

   - **Generate** `ENCRYPTION_KEY`: Run the provided `generate_key.py` script to create a Fernet encryption key for securing TRX private keys:

     ```bash
     python generate_key.py
     ```

     Copy the output and set it as `ENCRYPTION_KEY`. This key is critical for the wallet application’s security.

   - **ZarinPal Configuration**: The wallet application uses a sandbox ZarinPal merchant ID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`) for testing. For production, obtain a valid merchant ID from ZarinPal and update `ZARINPAL_MERCHANT_ID`.

   - **Email Configuration**: Use a valid email account (e.g., Gmail) for `EMAIL_HOST_USER` and an app-specific password for `EMAIL_HOST_PASSWORD`. Ensure `SUPPORT_EMAIL` is set to a valid email address for receiving contact form submissions.

   - **Redis Configuration**: Ensure Redis is running on the specified `REDIS_LOCATION` (default: `redis://127.0.0.1:6379/0`). Install Redis if not already present:

     - On Linux: `sudo apt-get install redis-server`
     - On Windows: Download from Redis Windows

   - **Security Note**: The `.env` file contains sensitive information and is included in `.gitignore` to prevent accidental commits to version control. Never share this file publicly.

2. **Database Configuration**:

   - The project defaults to SQLite (`db.sqlite3`), suitable for development. For production, consider using a more robust database like PostgreSQL by updating the `DATABASES` setting in `settings.py`:

     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'your_db_name',
             'USER': 'your_db_user',
             'PASSWORD': 'your_db_password',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```

3. **Logging Configuration**:

   - Logging is configured in `settings.py` to capture errors and search activities:
     - `error.log`: Stores error-level messages for debugging server or database issues.
     - `search_logs.log`: Logs search queries, particularly those with no results, for user behavior analysis.
   - These files are created in the project root directory upon first log event.

## Running the Project

1. **Start the Development Server**:

   ```bash
   python manage.py runserver
   ```

   The server will be available at \`\[invalid url, do not cite\].

2. **Access the Admin Panel**: Navigate to \`\[invalid url, do not cite\] and log in using the superuser credentials created earlier. The admin panel allows management of SimCards, comments, accounts, and contact form submissions.

3. **Interact with APIs**: The project provides RESTful APIs for all major functionalities, accessible via endpoints defined in each application’s `urls.py`:

   - `/api/simkart/`: SimCard listings, comments, and contact forms.
   - `/api/cart/`: Cart management, item addition/removal, and invoice creation.
   - `/api/wishlist/`: Wishlist management.
   - `/api/wallet/`: Wallet deposits, transaction verification, and cart payments. Use tools like Postman or `curl` to test these endpoints. Example request:

   ```bash
   curl -X GET http://localhost:8000/api/simkart/simcards/ -H "Authorization: Bearer your_jwt_token"
   ```

4. **Production Deployment**: For production, set `DJANGO_DEBUG=False` in `.env` and configure a production-ready web server (e.g., Gunicorn with Nginx). Ensure all environment variables are set correctly and use a secure database like PostgreSQL.

## Logging

The project implements real-time logging to track errors and user activities, configured in `settings.py`:

- `error.log`:
  - **Purpose**: Captures all error-level messages from Django and application components, such as server crashes, database errors, or API failures.
  - **Use Case**: Essential for debugging and identifying issues during development or production.
- `search_logs.log`:
  - **Purpose**: Records search-related activities, particularly queries that return no results, logged via the `search_logger` in `simkart/views.py`.
  - **Use Case**: Useful for analyzing user search behavior and improving search functionality.

To view logs, open the files in the project root directory using a text editor or command-line tools:

```bash
cat error.log
cat search_logs.log
```

Logs are stored in the project root and can be accessed directly. For advanced log analysis, consider integrating a log management tool like ELK Stack in production.

## Notes

- **Wallet Application Testing**: The wallet application is designed for testing purposes and uses sandbox environments:

  - **ZarinPal**: Utilizes a sandbox merchant ID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`). For production, obtain a valid merchant ID from ZarinPal and update `ZARINPAL_MERCHANT_ID` in `.env`.
  - **Tron**: Operates on the Shasta testnet for TRX transactions. For production, configure Tron for the mainnet by updating the network settings in `wallet/views.py`.

- **Configuration Placeholders**: Ensure all placeholders (e.g., `...`) in `.env` and `settings.py` are replaced with actual values before running the project. Critical variables include:

  - `DJANGO_SECRET_KEY`: Generate a secure key using:

    ```bash
    python -c "import secrets; print(secrets.token_urlsafe(50))"
    ```

  - `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`: Use a valid email account and app-specific password (e.g., Gmail app password).

  - `SUPPORT_EMAIL`: Set to a valid email address for receiving contact form submissions.

- **Virtual Environment**: Running the project in a virtual environment is mandatory to isolate dependencies and prevent conflicts with system-wide packages. This ensures consistent behavior across different development and production environments.

- **Django Version**: The project uses Django 4.2.20, requiring Python 3.8 or higher. Ensure your Python environment is compatible before installation.

- **Security Considerations**:

  - The `.env` file contains sensitive information and is included in `.gitignore` to prevent accidental exposure. Never commit this file to version control.
  - Use HTTPS in production to secure API communications.
  - Regularly rotate `ENCRYPTION_KEY` and other sensitive credentials.

## Unnecessary Libraries

The original `requirements.txt` included several libraries that appear unnecessary based on the provided project code, as they are not imported or used in the core functionality. These have been removed in the updated `requirements.txt`. Removed libraries include:

- `Flask`: A Python web framework irrelevant to this Django project.
- `selenium`: Used for browser automation or web scraping, not required for e-commerce functionality.
- `pywhatkit`: Supports automation tasks (e.g., WhatsApp messaging), not used in the project.
- `wikipedia`: Provides access to Wikipedia data, not utilized in the code.
- `PyAutoGUI`: For GUI automation, unsuitable for a web-based application.

To verify unused libraries, you can use pipdeptree to analyze dependencies:

```bash
pip install pipdeptree
pipdeptree
```

This tool displays the dependency tree, helping identify libraries not required by the project. Alternatively, manually review all project files for unused imports to ensure no essential libraries are removed.

## Contributing

Contributions to the Simkart project are welcome. To contribute:

1. Fork the repository and create a new branch for your feature or bug fix.

2. Follow the coding style and conventions used in the project (e.g., PEP 8 for Python).

3. Write tests for new features and ensure existing tests pass:

   ```bash
   python manage.py test
   ```

4. Submit a pull request with a clear description of your changes.

## Testing

The project includes no explicit test suite in the provided code, but you can add tests using Django’s testing framework. Place test files in each application’s `tests.py` or `tests/` directory. Run tests with:

```bash
python manage.py test
```

For API testing, use tools like Postman to send requests to endpoints and verify responses. Ensure Redis is running during tests, as it is used for caching and sessions.

## Deployment

For production deployment:

1. Set `DJANGO_DEBUG=False` in `.env`.
2. Use a production-ready web server like Gunicorn with Nginx as a reverse proxy.
3. Configure a robust database like PostgreSQL.
4. Secure the application with HTTPS using a service like Let’s Encrypt.
5. Monitor logs (`error.log`, `search_logs.log`) for issues and set up log rotation to manage file size.

Example Gunicorn command:

```bash
gunicorn --workers 3 simkart_project_f.wsgi:application --bind 0.0.0.0:8000
```

## Key Files and Directories

| File/Directory | Description | Location |
| --- | --- | --- |
| `.env` | Contains sensitive environment variables (e.g., API keys, email credentials) | Project root |
| `settings.py` | Django project settings, including database and logging configurations | `simkart_project_f/` |
| `generate_key.py` | Script to generate a Fernet encryption key for the wallet application | Project root |
| `error.log` | Logs error-level messages for debugging | Project root |
| `search_logs.log` | Logs search activities for user behavior analysis | Project root |
| `requirements.txt` | Lists project dependencies | Project root |

## Troubleshooting

- **Redis Connection Issues**: Ensure Redis is running on the specified port (default: 6379). Check with:

  ```bash
  redis-cli ping
  ```

  If you receive `PONG`, Redis is operational. Otherwise, start Redis:

  ```bash
  redis-server
  ```

- **Email Sending Failures**: Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env`. For Gmail, use an app-specific password.

- **ZarinPal Errors**: If payment requests fail, check `ZARINPAL_MERCHANT_ID` and ensure the ZarinPal sandbox or production environment is accessible.

- **API Authentication Issues**: Obtain a JWT token using the `/api/token/` endpoint and include it in API requests:

  ```bash
  curl -X POST http://localhost:8000/api/token/ -d "username=your_username&password=your_password"
  ```

For additional support, check the logs (`error.log`, `search_logs.log`) or consult the Django documentation.

## Key Citations

- Django Official Documentation: Comprehensive guide for Django settings and configuration.
- ZarinPal Sandbox Documentation: Details on using ZarinPal’s sandbox environment for payment testing.
- TronPy Library Documentation: Reference for interacting with the Tron blockchain using TronPy.
- Pipdeptree PyPI Page: Tool for analyzing Python project dependencies.
- Postman Official Website: API testing tool for interacting with RESTful endpoints.
- Gunicorn Documentation: Guide for deploying Django applications with Gunicorn.
- Nginx Official Website: Documentation for configuring Nginx as a reverse proxy.
- Let’s Encrypt Official Website: Free SSL/TLS certificates for securing web applications.