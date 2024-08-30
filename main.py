from __init__ import app

if __name__ == "__main__":

    # 한번만 실행되면 되는 코드들
    # DB 연결이나 Model Load 등

    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
