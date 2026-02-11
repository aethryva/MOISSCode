from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from moisscode.lexer import MOISSCodeLexer
from moisscode.parser import MOISSCodeParser
from moisscode.interpreter import MOISSCodeInterpreter
import traceback

app = FastAPI(title="MOISSCode API", version="1.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

from moisscode.modules.med_io import MedIO
from moisscode.stdlib import StandardLibrary

@app.get("/")
def read_root():
    return {"status": "MOISSCode Engine Online"}

@app.get("/devices")
def get_devices():
    return MedIO.devices.devices

@app.get("/finance")
def get_finance():
    return {
        "total": StandardLibrary.finance.get_total(),
        "ledger": StandardLibrary.finance.get_ledger()
    }

@app.post("/run")
def run_code(request: CodeRequest):
    print(f"Received code execution request ({len(request.code)} chars)")
    
    try:
        # 1. Lexing
        lexer = MOISSCodeLexer()
        tokens = lexer.tokenize(request.code)
        
        # 2. Parsing
        parser = MOISSCodeParser(tokens)
        program = parser.parse_program()
        
        # 3. Execution
        interpreter = MOISSCodeInterpreter()
        events = interpreter.execute(program)
        
        return {
            "status": "success",
            "events": events
        }
        
    except Exception as e:
        print(f"Execution Error: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }

if __name__ == "__main__":
    print(r"""
      ____       _          _    ___ 
     |  _ \ _ __(_)_   _   / \  |_ _|
     | |_) | '__| | | | | / _ \  | | 
     |  __/| |  | | |_| |/ ___ \ | | 
     |_|   |_|  |_|\__, /_/   \_\___|
                   |___/             
      ____             _   _            _ 
     / ___|  ___ _ __ | |_(_)_ __   ___| |
     \___ \ / _ \ '_ \| __| | '_ \ / _ \ |
      ___) |  __/ | | | |_| | | | |  __/ |
     |____/ \___|_| |_|\__|_|_| |_|\___|_|
                                          
    Aethryva Deeptech | MOISSCode Engine v1.0
    """)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
