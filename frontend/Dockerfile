# Build stage
FROM node:20-alpine AS build
WORKDIR /app
# Use files relative to the frontend build context
COPY package.json package-lock.json* /app/
RUN npm ci --quiet || npm install --quiet
COPY . /app

# Inject Auth0 Vite env at build time (optional)
ARG VITE_AUTH0_DOMAIN
ARG VITE_AUTH0_CLIENT_ID
ARG VITE_AUTH0_AUDIENCE
ENV VITE_AUTH0_DOMAIN=$VITE_AUTH0_DOMAIN \
    VITE_AUTH0_CLIENT_ID=$VITE_AUTH0_CLIENT_ID \
    VITE_AUTH0_AUDIENCE=$VITE_AUTH0_AUDIENCE

RUN npm run build

# Run stage (nginx)
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
