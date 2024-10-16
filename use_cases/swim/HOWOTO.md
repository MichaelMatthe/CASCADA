# SWIM - Docker

Make sure docker (desktop) is running.

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