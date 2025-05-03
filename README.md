## Architecture Overview
```
flowchart TD
  subgraph VPC
    subgraph Subnet1[Public Subnet 1]
      user_service["user_service (Lambda)"]
      api_gateway1["API Gateway"]
      jwt_db[("JWT Token DB (RDS Postgres, Public)")]
    end
    subgraph Subnet2[Public Subnet 2]
      resume_service["resume_service (Lambda)"]
      api_gateway2["API Gateway"]
      resume_db[("Resume Data DB (RDS Postgres, Public)")]
    end
  end
  event_bridge["Event Bridge"]

  api_gateway1 -->|"HTTP requests"| user_service
  user_service -->|"DB connections"| jwt_db
  api_gateway2 -->|"HTTP requests"| resume_service
  resume_service -->|"DB connections"| resume_db
  event_bridge -->|"Scheduled event (midnight)"| user_service

```
```

Key components shown:
- **VPC structure** with two public subnets containing services
- **Lambda-API Gateway connections** for both services
- **Public RDS instances** clearly labeled with their purposes
- **Event Bridge trigger** specifically targeting user_service

Security recommendation: While this diagram reflects your current public RDS setup, consider moving databases to private subnets and restricting access through security groups for production environments.
