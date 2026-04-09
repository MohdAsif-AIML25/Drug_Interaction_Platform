# Use official node image
FROM node:18-slim AS builder

WORKDIR /app

# Install dependencies first (for caching)
COPY package.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Use Nginx to serve the build
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# If you have routing, copy a custom nginx config
# COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
