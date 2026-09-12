# Build stage - Maven
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /app

# Copy pom.xml
COPY pom.xml .

# Download dependencies (cached layer)
RUN mvn dependency:resolve-plugins dependency:resolve

# Copy source code
COPY src ./src

# Build the application with Lombok processing enabled
RUN mvn clean package -DskipTests \
    -Dlombok.delombok.skip=false \
    -Dlombok.addLombokGeneratedAnnotation=true

# Runtime stage - OpenJDK 21
FROM eclipse-temurin:21-jre-jammy

# Install curl for the container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy JAR from builder stage
COPY --from=builder /app/target/pulseai-server-*.jar app.jar

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:8080/api/v1/auth/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
