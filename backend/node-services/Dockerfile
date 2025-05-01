FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Fix permissions for executables in node_modules/.bin
RUN chmod -R 755 ./node_modules/.bin

EXPOSE 8000

# Use npm start for production (uses node directly instead of nodemon)
CMD ["npm", "start"]
