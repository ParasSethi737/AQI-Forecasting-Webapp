# Stage 1: Build the app
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of your application code
COPY . .

# Build the app using Vite
RUN npm run build

# Stage 2: Serve the app using NGINX
FROM nginx:alpine

# Copy the built app from the build stage to the NGINX directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy your custom nginx configuration if you have one (optional)
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port that NGINX will run on
EXPOSE 80

# Run NGINX in the foreground
CMD ["nginx", "-g", "daemon off;"]