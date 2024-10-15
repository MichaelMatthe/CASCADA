# Tested setup / Requirements

- WSL on Windows 11 running Ubuntu 22.04.4 LTS, Python 3.11.1
    - Clone repository into linux filesystem not into the windows file system! (e.g. not in /mnt/c/...) Increases code execution speed a lot!
- Docker
    - gabrielmoreno/swim
- Java (DeltaIoT)

## How to run swim example

### Docker

Install Docker.

Make sure Docker (desktop) is running.

Run docker container (add port 4242 for external adaptation control)

```powershell
docker run -d -p 5901:5901 -p 6901:6901 -p 4242:4242 --name swim gabrielmoreno/swim
```

If the container name "/swim" is already in use: find the container ID and restart the container.

```powershell
docker ps -a
docker restart swim
```

Go to:
http://localhost:6901
pw: vncpassword

Open Terminal Emulator

Inside container - start simulation:
```powershell
cd ~/seams-swim/swim/simulations/swim/
./run.sh sim 1
```

Alternatively without web application over terminal
```powershell
docker exec -it swim sh
```

### CASCADA Framework

(On windows start WSL in Powershell / Command Line.)

Clone repository into WSL file structure e.g. "~/" and not "/mnt/c/..."

Install python 3.11, virtual environment and requirements:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start SWIM Server (see Docker above), then run:

```
python3 swim_eval.py
```
