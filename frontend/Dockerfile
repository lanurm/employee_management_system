# ============================================
# Frontend - Nginx Dockerfile
# ============================================
# Serves static files for the Employee Management System frontend

FROM node:20-alpine AS builder

WORKDIR /app

# Copy frontend files
COPY . .

# No build step needed for vanilla JS, just ensure files exist
RUN echo "Frontend files ready for serving"


# Production stage - Nginx server
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy frontend files from builder stage
COPY --from=builder /app /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
