#!/usr/bin/env python3

import uvicorn


if __name__ == "__main__":
    uvicorn.run("ff2.app_main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="debug",
            #debug=True,
            workers=1,
            limit_concurrency=10,
            limit_max_requests=10)
