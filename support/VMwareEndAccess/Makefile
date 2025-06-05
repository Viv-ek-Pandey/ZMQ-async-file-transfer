INCLUDEDIR=/opt/dmservice/vmware_lib/include/
LIBDIR=/opt/dmservice/vmware_lib/lib64/
LIBS=-ldl -lz -lsqlite3 -lcurl -lssl -lcrypto -lcares
#LDFLAGS=-Wl

unlockVM: UnlockVM.c
	gcc -o $@ -I$(INCLUDEDIR) -L$(LIBDIR) $? $(LIBS) -lvixDiskLib
clean:
	@rm -rf unlockVM
