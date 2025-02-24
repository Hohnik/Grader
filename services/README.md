# Server Admin
Start server by running
```sh
uvicorn api.main:app --reload
```
# Teacher
Upload a dockerfile to the registry 
    - the students code is mounted to `/app/src/`.
    - write the output to `/app/output/score.txt`.

