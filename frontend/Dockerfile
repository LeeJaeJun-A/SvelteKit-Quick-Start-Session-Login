# Use the official Node.js image as a parent image
FROM node:20

# Set the working directory inside the container
WORKDIR /app/frontend

# Copy the entire frontend directory into the container at /app/frontend
COPY . /app/frontend

# Install dependencies
RUN npm install

# Build the SvelteKit application
RUN npm run build

# Expose port 4173 for the SvelteKit application
EXPOSE 4173

# Command to run the SvelteKit application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
