## 1. Install dependencies

```bash
pip install -r requirements.txt
````

## 2. Set required environment variable

The app expects the environment variable `BWAI_MCP_SERVER_URL` to be set.
You can define it in either of the following ways:

### Option A: Set it in your shell environment

```bash
export BWAI_MCP_SERVER_URL=https://your-server-url.com
```

### Option B: Define it in a `.env` file

Create a file named `.env` in the project directory with the following content:

```
BWAI_MCP_SERVER_URL=https://your-server-url.com
```

## 3. Start the app

Run the app:

```bash
python app.py
```

It will print the URL it’s running on, such as:

```
Running on http://localhost:5001
```

## 4. Open in your browser

Open the specified URL (with the correct port) in your web browser:

```
http://localhost:5001
```
