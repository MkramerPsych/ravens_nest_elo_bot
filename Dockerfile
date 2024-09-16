FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && apt-get clean

RUN curl -sSf https://rye.astral.sh/get | RYE_TOOLCHAIN_VERSION="3.12" RYE_INSTALL_OPTION="--yes" bash
ENV PATH="/root/.rye/shims:/root/.rye/bin:$PATH"

WORKDIR /app
RUN git clone https://github.com/MkramerPsych/ravens_nest_elo_bot.git
WORKDIR /app/ravens_nest_elo_bot

RUN rye pin cpython@3.12.0
RUN rye sync

ENV DISCORD_BOT_TOKEN="MTI4MzY5MDQ3NDY1MzIyMDg3NQ.Gr1qhj.4n8qOWQu8nxV2zqltJaSwQ_M9mFxlZQgSh_D-Q"
ENV ADMIN_PASSWD="ALLMIND"

CMD ["rye", "run", "ravens_nest_bot"]
