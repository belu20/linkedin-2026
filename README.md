# Run Engine (Windows)
set VM=WIKA && set PORT=1561 && set CLIENT_ID=36033 && python api.py
set VM=DEXA && set PORT=1562 && set CLIENT_ID=43924 && python api.py
set VM=IMF && set PORT=1563 && set CLIENT_ID=49716 && python api.py
set VM=GRAB && set PORT=1564 && set CLIENT_ID=48660 && python api.py

A Python-based crawler designed to collect LinkedIn posts (both personal and group posts) using two methods:

- HTML Request + BeautifulSoup (for public posts).
- Selenium (for private posts requiring login and interaction).

This project is packaged with Docker to ensure reliable deployment and scheduling.

---

## Features
- Crawl public and private LinkedIn posts.
- HTML request + BeautifulSoup for public posts (fast and efficient).
- Selenium for private posts (automates login and handles page rendering).
- Extract metadata: username, post ID, caption, reaction count, comment count, etc.
- Save results into Kafka.

---

## Preparation

### 1. Copy the environment file
```bash
cp .env.example .env
```

### 2. Edit the `.env` file with your configuration
```env
# MongoDB Database
MONGO_USER=admin
MONGO_PASS=your_secure_password
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB_ACCOUNT=account
MONGO_COLLECTION_ACCOUNT=linkedin

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=linkedin_posts

# Git Info
GIT_COMMIT_ID=abc123def
```

---

## Run with Docker Compose

### 1. Build and start all services
```bash
docker-compose up -d
```

### 2. View crawler logs
```bash
docker-compose logs -f likedin-search
```

---

## Useful Commands

### View container status
```bash
docker-compose ps
```

### View real-time logs
```bash
docker-compose logs -f likedin-search
```

### Restart a specific service
```bash
docker-compose restart likedin-search
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes (WARNING: data will be lost)
```bash
docker-compose down -v
```

### Rebuild container after code changes
```bash
docker-compose build likedin-search
```
```bash
docker-compose up -d --no-deps likedin-search
```

---

## Project Structure
```
project/
├── Dockerfile
├── docker-compose.yml
├── api.py
├── setting.py
├── run.sh
├── .env
├── .env.example
└── .dockerignore
```

---

## Important Tips

- **Selenium Setup** Ensure you have the correct browser driver installed (`chromedriver` or `geckodriver`) to work with Selenium.
- **Kafka**:
  - Ensure `KAFKA_BOOTSTRAP_SERVERS` points to a reachable broker (e.g., `kafka:9092` inside Docker or `localhost:9092` locally).
  - Verify topic exists (`linkedin_post`), or enable auto-topic-creation in Kafka.
  - Use `kafka-console-consumer` to test consumed messages: `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic linkedin_post --from-beginning`
- **MongoDB Data** is stored in the Docker volume `mongodb-data`, so your data persists even after container restarts.
- **MongoDB Port** (27017) is exposed so you can access it externally using MongoDB Compass.
- **Security**:
  - Change the default MongoDB password in the `.env` file.
  - Do not commit your `.env` file to version control.
  - Use a non-root user in your Dockerfile.
- **Monitoring**:
  - Use `docker-compose logs -f` to monitor the bot's activity in real-time.

---

## Troubleshooting

### Selenium Error
- Cause: Chromium renderer runs out of memory.
- Solution: Increase shared memory in Docker (shm_size: 512m) and block heavy resources.

### Database Connection Issue
```bash
docker-compose ps
docker-compose logs mongodb
docker-compose logs mysql
```

### Kafka not receiving messages
- Ensure broker is accessible.
- Confirm topic exists and matches `KAFKA_TOPIC` in `.env`.
- Check producer logs for connection errors.

### Container crashes due to memory issues
Add memory limits in `docker-compose.yml`:
```yaml
services:
  likedin-search:
    mem_limit: 1.5g
```

---

## Check Your IP (if using proxy/tunnel)
- [https://whatismyip.com](https://whatismyip.com)
- [https://ipinfo.io](https://ipinfo.io)

---

## License
This project uses the MIT license. Feel free to use and modify it as needed.

---

## Contributing
Pull requests and issues are welcome! Please fork the repo and create a new branch when making large changes.

# linkedin-2024-main



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/user/project/repository/web_editor/#create-a-file) or [upload](https://docs.gitlab.com/user/project/repository/web_editor/#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/rikizeinprojects/linkedin-2024-main.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://gitlab.com/rikizeinprojects/linkedin-2024-main/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/)
* [Automatically close issues from merge requests](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
e820ae53fffe92f9f37e31ca1bf7d1c6d58f4538
