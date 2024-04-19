# Use Ubuntu 20.04 as a base image
FROM node:20.10.0


# Set up a working directory
WORKDIR /app

COPY . .

RUN chmod -R 777 /app

RUN npm install

EXPOSE 3000

CMD ["npm", "run", "start"]
