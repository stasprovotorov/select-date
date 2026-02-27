FROM node:20
WORKDIR /client
ARG PUBLIC_IP
ENV NEXT_PUBLIC_CLIENT_BASE_URL="http://${PUBLIC_IP}:3000"
ENV NEXT_PUBLIC_SERVER_BASE_URL="http://${PUBLIC_IP}:8000"
ENV APP_BASE_URL="http://${PUBLIC_IP}:3000"
ENV CLIENT_URL="http://${PUBLIC_IP}:3000"
ENV NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]
