alias dev_run="docker container run -l dev-ssh-reg --name dev-ssh-reg --rm -itd -v $PWD/private/:/app/admin ssh-reg"
alias dev_stop="docker container stop $(docker ps -a -q --filter ancestor=ssh-reg --format='{{.ID}}')"
alias dev_build="docker build -t ssh-reg:latest --force-rm ."
alias dev_bash="docker container exec -it dev-ssh-reg bash -c 'cd /app/admin; exec bash --login -i'"
