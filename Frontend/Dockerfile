FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code (not needed if using volumes in development)
COPY . .

EXPOSE 3000

# Use development server
CMD ["npm", "start"]