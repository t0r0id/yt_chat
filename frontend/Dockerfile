# Use an official Node.js runtime as a parent image
FROM node:18.17.0-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install app dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Build the Next.js app for production
RUN npm run build

# Expose the port that the app will run on
EXPOSE 3000

# Define the command to run your application
CMD ["npm", "start"]
