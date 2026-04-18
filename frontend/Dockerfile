FROM node:22-slim

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Install dependencies first (layer caching)
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install

# Copy source
COPY . .

EXPOSE 3000

CMD ["pnpm", "dev"]
