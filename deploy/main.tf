# Terraform configuration for OCI Vosk STT API service

terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
      version = ">= 4.0"
    }
  }
}

# OCI Resource Manager automatically provides authentication
provider "oci" {
  region = var.region
}

# Locals for derived values
locals {
  # Derive create_vcn from network_strategy
  create_vcn = contains([
    "Create New VCN and Subnet", 
    "Create Minimal VCN and Subnet"
  ], var.network_strategy)
  
  # Determine if this is a minimal VCN setup
  is_minimal_vcn = var.network_strategy == "Create Minimal VCN and Subnet"
  
  # Use network_compartment_id if provided, otherwise use compartment_id
  network_compartment_id = var.network_compartment_id != "" ? var.network_compartment_id : var.compartment_id
  
  # Smart image selection logic
  selected_image_id = (
    var.compute_image_strategy == "Platform Image" ? (
      var.platform_image_ocid != "" ? var.platform_image_ocid : (
        length(data.oci_core_images.oracle_linux.images) > 0 ? 
        data.oci_core_images.oracle_linux.images[0].id : 
        data.oci_core_images.oracle_linux_fallback.images[0].id
      )
    ) : var.custom_image_ocid
  )
}

# Get the latest Oracle Linux 8 image for the region
data "oci_core_images" "oracle_linux" {
  compartment_id = var.compartment_id
  operating_system = "Oracle Linux"
  operating_system_version = "8"
  # Remove shape filter as it might be too restrictive
  sort_by = "TIMECREATED"
  sort_order = "DESC"
  
  filter {
    name   = "state"
    values = ["AVAILABLE"]
  }
}

# Backup: Get any Oracle Linux image if the above doesn't work
data "oci_core_images" "oracle_linux_fallback" {
  compartment_id = var.compartment_id
  operating_system = "Oracle Linux"
  sort_by = "TIMECREATED"
  sort_order = "DESC"
  
  filter {
    name   = "state"
    values = ["AVAILABLE"]
  }
}

# Image selection logic
locals {
  # Choose image based on strategy and availability
  selected_image_id = var.image_id != "" ? var.image_id : (
    var.compute_image_strategy == var.compute_image_strategy_enum["PLATFORM_IMAGE"] ? (
      var.platform_image_ocid != "" ? var.platform_image_ocid : (
        length(data.oci_core_images.oracle_linux.images) > 0 ? 
        data.oci_core_images.oracle_linux.images[0].id : 
        data.oci_core_images.oracle_linux_fallback.images[0].id
      )
    ) : var.custom_image_ocid
  )
}

# Create VCN if network strategy requires it
resource "oci_core_vcn" "stt_vcn" {
  count = local.create_vcn ? 1 : 0
  compartment_id = local.network_compartment_id
  display_name = local.is_minimal_vcn ? "vosk-stt-minimal-vcn" : "vosk-stt-vcn"
  cidr_blocks = [local.is_minimal_vcn ? "10.1.0.0/16" : "10.0.0.0/16"]
  dns_label = local.is_minimal_vcn ? "vosksttmin" : "voskstt"
  
  freeform_tags = local.is_minimal_vcn ? {
    "Purpose" = "Vosk-STT-Minimal"
    "FreeTier" = "true"
  } : {}
}

# Create subnet if network strategy requires it
resource "oci_core_subnet" "stt_subnet" {
  count = local.create_vcn ? 1 : 0
  compartment_id = local.network_compartment_id
  vcn_id = oci_core_vcn.stt_vcn[0].id
  display_name = local.is_minimal_vcn ? "vosk-stt-minimal-subnet" : "vosk-stt-subnet"
  cidr_block = local.is_minimal_vcn ? "10.1.1.0/24" : "10.0.1.0/24"
  dns_label = local.is_minimal_vcn ? "sttsubmin" : "sttsubnet"
  route_table_id = oci_core_route_table.stt_route_table[0].id
  security_list_ids = [oci_core_security_list.stt_api_security_list.id]
  
  # For minimal VCN, add Free Tier tags
  freeform_tags = local.is_minimal_vcn ? {
    "Purpose" = "Vosk-STT-Minimal"
    "FreeTier" = "true"
  } : {}
}

# Internet Gateway
resource "oci_core_internet_gateway" "stt_igw" {
  count = local.create_vcn ? 1 : 0
  compartment_id = local.network_compartment_id
  vcn_id = oci_core_vcn.stt_vcn[0].id
  display_name = local.is_minimal_vcn ? "vosk-stt-minimal-igw" : "vosk-stt-igw"
  
  freeform_tags = local.is_minimal_vcn ? {
    "Purpose" = "Vosk-STT-Minimal"
    "FreeTier" = "true"
  } : {}
}

# Route Table
resource "oci_core_route_table" "stt_route_table" {
  count = local.create_vcn ? 1 : 0
  compartment_id = local.network_compartment_id
  vcn_id = oci_core_vcn.stt_vcn[0].id
  display_name = local.is_minimal_vcn ? "vosk-stt-minimal-rt" : "vosk-stt-route-table"
  
  route_rules {
    destination = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.stt_igw[0].id
  }
  
  freeform_tags = local.is_minimal_vcn ? {
    "Purpose" = "Vosk-STT-Minimal"
    "FreeTier" = "true"
  } : {}
}

# Security list rules
resource "oci_core_security_list" "stt_api_security_list" {
  compartment_id = local.network_compartment_id
  display_name = "stt-api-security-list"
  vcn_id = local.create_vcn ? oci_core_vcn.stt_vcn[0].id : var.vcn_id
  
  egress_security_rules {
    protocol = "all"
    destination = "0.0.0.0/0"
    stateless = false
    description = "Allow all outbound traffic"
  }
  
  ingress_security_rules {
    protocol = "6"
    source = "0.0.0.0/0"
    stateless = false
    description = "Allow SSH"
    tcp_options {
      min = 22
      max = 22
    }
  }
  
  ingress_security_rules {
    protocol = "6"
    source = "0.0.0.0/0"
    stateless = false
    description = "Allow HTTP traffic"
    tcp_options {
      min = 80
      max = 80
    }
  }
  
  ingress_security_rules {
    protocol = "6"
    source = "0.0.0.0/0"
    stateless = false
    description = "Allow HTTPS traffic"
    tcp_options {
      min = 443
      max = 443
    }
  }
  
  ingress_security_rules {
    protocol = "6"
    source = "0.0.0.0/0"
    stateless = false
    description = "Allow API traffic"
    tcp_options {
      min = 8000
      max = 8000
    }
  }
}

# Cloud-init script for Docker installation and service startup
locals {
  cloud_init = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    api_key = var.api_key
    docker_image = var.docker_image_name
    github_repo_url = var.github_repo_url
  }))
}

# Compute instance
resource "oci_core_instance" "stt_api_instance" {
  availability_domain = var.availability_domain
  compartment_id = var.compartment_id
  display_name = "vosk-stt-api"
  shape = var.vm_shape
  
  # Flexible shape configuration
  dynamic "shape_config" {
    for_each = length(regexall("Flex", var.vm_shape)) > 0 ? [1] : []
    content {
      ocpus = var.vm_ocpus
      memory_in_gbs = var.vm_memory_gb
    }
  }
  
  create_vnic_details {
    subnet_id = local.create_vcn ? oci_core_subnet.stt_subnet[0].id : var.subnet_id
    assign_public_ip = true
    display_name = "vosk-stt-vnic"
  }
  
  source_details {
    source_type = "image"
    source_id = local.selected_image_id
  }
  
  metadata = {
    ssh_authorized_keys = var.ssh_authorized_keys
    user_data = local.cloud_init
  }
  
  timeouts {
    create = "30m"
  }
}

# Output values
output "instance_public_ip" {
  description = "Public IP address of the STT API instance"
  value = oci_core_instance.stt_api_instance.public_ip
}

output "instance_private_ip" {
  description = "Private IP address of the STT API instance"
  value = oci_core_instance.stt_api_instance.private_ip
}

output "api_url" {
  description = "URL to access the STT API"
  value = "http://${oci_core_instance.stt_api_instance.public_ip}:8000"
}

output "api_docs_url" {
  description = "URL to access the API documentation"
  value = "http://${oci_core_instance.stt_api_instance.public_ip}:8000/docs"
}

output "image_used" {
  description = "Image ID used for the instance"
  value = local.selected_image_id
}

output "deployment_info" {
  description = "Deployment information and next steps"
  value = {
    instance_ip = oci_core_instance.stt_api_instance.public_ip
    api_url = "http://${oci_core_instance.stt_api_instance.public_ip}:8000"
    docs_url = "http://${oci_core_instance.stt_api_instance.public_ip}:8000/docs"
    ssh_command = "ssh opc@${oci_core_instance.stt_api_instance.public_ip}"
    logs_command = "sudo tail -f /var/log/vosk-stt-deployment.log"
  }
}