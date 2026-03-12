# dev
# FROM node:20-alpine
# WORKDIR /frontend

# COPY package.json package-lock.json ./

# RUN npm ci

# COPY . .

# EXPOSE 3000

# CMD ["npm", "start"]

# prod
# 1. Build stage
FROM node:20-alpine AS build

WORKDIR /frontend

# Copy package files first (for caching)
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the production React app
RUN npm run build

# 2. Nginx stage
FROM nginx:alpine

# Remove default content
RUN rm -rf /usr/share/nginx/html/*

# Copy React build
COPY --from=build /frontend/build /usr/share/nginx/html

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
