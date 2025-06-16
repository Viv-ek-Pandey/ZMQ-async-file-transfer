#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stdbool.h>
#include <vm_basic_types.h>
#include "vixDiskLib.h"

void usage() {
    printf("Usage: ./unlockVM <vcenter> <username> <password> <vm-moref>\n");
    exit(1);
}

void warningLogFunc(const char *fmt, va_list args) {
    printf("Warning: ");
    vprintf(fmt, args);
}

void genericLogFunc(const char *fmt, va_list args) {
    printf("Log: ");
    vprintf(fmt, args);
}

void panicLogFunc(const char *fmt, va_list args) {
    printf("Panic: ");
    vprintf(fmt, args);
}

void logVddkError(VixError vixError) {
    char *vddk_err_msg = VixDiskLib_GetErrorText(vixError, NULL);
    if (vddk_err_msg) {
        printf("\nError Code: %lu :: %s\n", vixError, vddk_err_msg);
        VixDiskLib_FreeErrorText(vddk_err_msg);
    }
}

VixError dmVddkInitEx(uint32 majorVersion, uint32 minorVersion, const char *libDir, const char *configFile) {
    VixError vixError = VixDiskLib_InitEx(
        majorVersion,
        minorVersion,
        &genericLogFunc,
        &warningLogFunc,
        &panicLogFunc,
        libDir,
        configFile
    );

    if (vixError != VIX_OK) {
        printf("\nVDDK InitEx Error:");
        logVddkError(vixError);
    }

    return vixError;
}

void dmVddkUnload(void) {
    VixDiskLib_Exit();
}

char* getHostCertificate(const char* hostname) {
    static char cert[256];
    char command[512];
    FILE *fp;

    snprintf(command, sizeof(command),
             "echo | openssl s_client -connect %s:443 2>/dev/null | "
             "openssl x509 -noout -fingerprint -sha1 | cut -d '=' -f2",
             hostname);

    fp = popen(command, "r");
    if (fp == NULL) {
        perror("Failed to run command");
        return NULL;
    }

    if (fgets(cert, sizeof(cert), fp) == NULL) {
        pclose(fp);
        return NULL;
    }

    pclose(fp);

    // Clean whitespace
    size_t j = 0;
    for (size_t i = 0; i < strlen(cert); ++i) {
        if (cert[i] != ' ' && cert[i] != '\n') {
            cert[j++] = cert[i];
        }
    }
    cert[j] = '\0';

    return cert;
}

VixError dmEndAccess(VixDiskLibConnectParams *cnxParams, const char *identity) {
    VixError vixError = VixDiskLib_EndAccess(cnxParams, identity);
    if (vixError != VIX_OK) {
        printf("\nFailed to EndAccess:");
        logVddkError(vixError);
    }
    return vixError;
}

int main(int argc, char *argv[]) {
    if (argc != 5) usage();

    const char* vcenter   = argv[1];
    const char* username  = argv[2];
    const char* password  = argv[3];
    const char* vm_moref  = argv[4];

    printf("Initializing VDDK...\n");
    VixError err = dmVddkInitEx(
        7, 0, // VDDK version
        "/opt/dmservice/vmware_lib/",
        "/opt/dmservice/conf/initex.conf"
    );

    if (err != VIX_OK) {
        printf("\nInitialization failed.");
        return 1;
    }

    printf("\nInitialized successfully.");

    // Allocate and fill VixDiskLibConnectParams
    VixDiskLibConnectParams *params = VixDiskLib_AllocateConnectParams();
    if (!params) {
        printf("VDDK ConnectEx Error: Failed to allocate connect params.");
        logVddkError(VIX_E_OUT_OF_MEMORY);
        return VIX_E_OUT_OF_MEMORY;
    }

    params->specType = VIXDISKLIB_SPEC_VMX;

    // Correct string construction for vmxSpec
    char vmxSpecBuffer[256];
    snprintf(vmxSpecBuffer, sizeof(vmxSpecBuffer), "moref=%s", vm_moref);
    params->vmxSpec = vmxSpecBuffer;

    params->serverName  = (char*)vcenter;
    params->port        = 443;
    params->thumbPrint  = getHostCertificate(vcenter);
    params->credType    = VIXDISKLIB_CRED_UID;
    params->creds.uid.userName = (char*)username;
    params->creds.uid.password = (char*)password;
    params->nfcHostPort = 902;

    printf("\nCalling EndAccess on VM...");
    err = dmEndAccess(params, "DM-REPL-ACCESS");
    if (err != VIX_OK) {
        printf("\nUnlock VM Failed:");
        return 1;
    }

    printf("\nUnlocked VM Successfully.\n");

    dmVddkUnload();
    printf("\nDONE!\n");

    return 0;
}
