# Stage 1: Build the Vue application
FROM node:22-alpine as build-stage

WORKDIR /app

COPY package*.json ./

# Assuming package.json exists. If not, this step will fail.
# Since we are just scaffolding, we will handle the absence of package.json by initializing a dummy one if needed later,
# but for now I will assume the user or I will generate it.
# For the purpose of "Deliverable", I will assume standard structure.

RUN npm install

COPY . .

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:stable-alpine as production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
