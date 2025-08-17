# OCI Deployment Troubleshooting Guide

## Common Deployment Issues and Solutions

### 1. "404-NotAuthorizedOrNotFound" Error

**Error Message:**
```
Error: 404-NotAuthorizedOrNotFound, Authorization failed or requested resource not found.
```

**Root Causes & Solutions:**

#### A. Incorrect Compartment Selection
- **Problem**: Using tenancy OCID instead of compartment OCID
- **Solution**: In the Resource Manager form, select a proper compartment from the dropdown
- **Note**: The compartment dropdown should show compartment names, not OCIDs

#### B. Insufficient Permissions
- **Problem**: User lacks required permissions in the target compartment
- **Required Permissions**: You need the following IAM policies:

```
Allow group <YourGroup> to manage virtual-network-family in compartment <CompartmentName>
Allow group <YourGroup> to manage compute-family in compartment <CompartmentName>
Allow group <YourGroup> to manage instance-family in compartment <CompartmentName>
```

**Minimum Permissions for Free Tier:**
```
Allow group <YourGroup> to use virtual-network-family in compartment <CompartmentName>
Allow group <YourGroup> to manage instances in compartment <CompartmentName>
Allow group <YourGroup> to manage volumes in compartment <CompartmentName>
```

#### C. Regional Resource Limits
- **Problem**: Target region has reached resource limits
- **Solution**: Try a different region or request service limit increase

### 2. Image Selection Issues

**Error:** Image not found or unavailable

**Solutions:**
- For **Platform Images**: Ensure the selected OS is available in your region
- For **Custom Images**: Verify the OCID is correct and accessible
- Use the **Auto-detect** option for most reliable deployment

### 3. Network Configuration Errors

**Error:** VCN or Subnet creation failures

**Solutions:**
- Ensure CIDR blocks don't overlap with existing networks
- Verify availability domain selection
- Check regional subnet limits

## Pre-Deployment Checklist

### 1. OCI Account Setup
- [ ] Free Tier account activated
- [ ] Required service limits available
- [ ] Target compartment exists

### 2. IAM Permissions
- [ ] User belongs to appropriate group
- [ ] Group has required policies
- [ ] Compartment-level permissions verified

### 3. Resource Manager Configuration
- [ ] Correct compartment selected (not tenancy)
- [ ] Valid availability domain chosen
- [ ] API key meets requirements (16+ chars)
- [ ] Network configuration validated

## Deployment Best Practices

### 1. Start with Defaults
- Use default values for first deployment
- Test with VM.Standard.A1.Flex (Free Tier)
- Let the system auto-detect images

### 2. Progressive Configuration
1. **Basic Deployment**: Default settings, no SSH
2. **SSH Access**: Add SSH key after basic deployment works
3. **Custom Images**: Use only after platform images succeed
4. **Existing Networks**: Use only if you understand OCI networking

### 3. Resource Cleanup
- Always destroy test deployments
- Monitor Free Tier usage
- Use Resource Manager's "Destroy" action

## Regional Considerations

### Free Tier Availability
Free Tier resources are not available in all regions. Recommended regions:
- **US East (Ashburn)**: `us-ashburn-1`
- **US West (Phoenix)**: `us-phoenix-1`  
- **UK South (London)**: `uk-london-1`
- **Germany Central (Frankfurt)**: `eu-frankfurt-1`
- **Japan East (Tokyo)**: `ap-tokyo-1`

### Image Availability
Platform images may vary by region. The auto-detection feature handles this automatically.

## Support Resources

### OCI Documentation
- [Resource Manager Overview](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm)
- [IAM Policies](https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/policyreference.htm)
- [Free Tier Information](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)

### Project Resources
- [Main Repository](https://github.com/kouko/oci-vosk-speech2text-api-service)
- [Technical Documentation](../TDD.md)
- [API Documentation](../API.md)

## Quick Fix for Common Error

If you see the "404-NotAuthorizedOrNotFound" error:

1. **Go back to the Resource Manager form**
2. **In the "Target Compartment" field**: Click the dropdown and select a named compartment (not root)
3. **Verify the compartment name** appears in the dropdown (not an OCID)
4. **If no compartments appear**: Your user lacks compartment listing permissions
5. **Contact your OCI administrator** to grant proper permissions

## Still Having Issues?

1. Check the [GitHub Issues](https://github.com/kouko/oci-vosk-speech2text-api-service/issues)
2. Review OCI Free Tier limits
3. Try a different region
4. Contact OCI Support for account-specific issues
