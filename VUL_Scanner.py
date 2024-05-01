import yaml

# YAML configuration as a string
yaml_data = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: bigleu007/myapp
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
  - name: app-myapp
    port: 3000
    targetPort: 3000
"""

# Load the YAML into Python data structures
documents = list(yaml.safe_load_all(yaml_data))

# Function to analyze the Kubernetes configuration
def analyze_k8s_config(documents):
    results = []
    for doc in documents:
        if doc['kind'] == "Deployment":
            containers = doc['spec']['template']['spec']['containers']
            for container in containers:
                if 'ports' in container:
                    for port in container['ports']:
                        results.append(f"Container '{container['name']}' exposes port {port['containerPort']}.")

                # Resource checks
                if 'resources' not in container:
                    results.append(f"Container '{container['name']}' does not have resource limits set.")
                    results.append("Solution: Define CPU and memory requests and limits in the container spec.")
                
                # Probes checks
                if 'livenessProbe' not in container:
                    results.append(f"No livenessProbe set for '{container['name']}'.")
                    results.append("Solution: Add a livenessProbe to the container spec to check the health of the application.")
                if 'readinessProbe' not in container:
                    results.append(f"No readinessProbe set for '{container['name']}'.")
                    results.append("Solution: Add a readinessProbe to ensure the container does not receive traffic before it is ready.")

        elif doc['kind'] == "Service":
            # LoadBalancer checks
            if doc['spec']['type'] == "LoadBalancer":
                results.append("Service type is LoadBalancer, which provides an external load-balanced IP.")
            else:
                results.append(f"Service '{doc['metadata']['name']}' does not use a LoadBalancer; it uses {doc['spec']['type']} type instead.")
                results.append("Solution: Change the service type to 'LoadBalancer' if external access is needed with load balancing.")
            
            for port in doc['spec']['ports']:
                results.append(f"Service maps port {port['port']} to target port {port['targetPort']}.")

    # RBAC checks
    rbac_present = any(doc['kind'] in ["Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding"] for doc in documents)
    if not rbac_present:
        results.append("RBAC settings are not defined for specific user access.")
        results.append("Solution: Define appropriate roles and role bindings to restrict access based on least privilege principle.")

    return results

# Print the analysis results
analysis_results = analyze_k8s_config(documents)
for result in analysis_results:
    print(result)
