# We must allow others exactly use our script without modification
# Or its not replicable by others.
#
REGISTRY=docker.io
REPOSITORY=centerforopenneuroscience

IMAGE_NAME=mvmnda
IMAGE_TAG=0.0.1

FQDN_IMAGE=${REGISTRY}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}

# PATH for scratch directory storing intermidiate results etc;
# By default -- all data including intermediate results are under this folder (YODA!)
#ifeq ($(SCRATCH_PATH),)
#	SCRATCH_PATH = /var/tmp/mvmnda/
#endif

OCI_BINARY?=podman
RELEASE_VERSION?=9999
RESOLUTION?=9999 # specified in microns
SING_BINARY?=singularity
PACKAGE_NAME=mvmnda

DISTFILE_CACHE_CMD :=

check_defined = \
    $(strip $(foreach 1,$1, \
        $(call __check_defined,$1,$(strip $(value 2)))))
__check_defined = \
    $(if $(value $1),, \
      $(error Undefined $1$(if $2, ($2))))

ifeq ($(DISTFILE_CACHE_PATH),)
    # If not set, don't add it as an option
else
    DISTFILE_CACHE_CMD =-v $(DISTFILE_CACHE_PATH):/var/cache/distfiles
endif

.PHONY: data
data: clean
	python reposit.py

.PHONY: data-oci
data-oci: clean
	$(OCI_BINARY) run \
		-it \
		--rm \
		-v ${PWD}/../..:/root/src/mvmnda \
		--workdir /root/src/mvmnda/rawdata/code \
		${FQDN_IMAGE} \
		make data

.PHONY: data-oci-interactive
data-oci-interactive: clean
	$(OCI_BINARY) run \
		-it \
		--rm \
		-v ${PWD}/../..:/root/src/mvmnda \
		--workdir /root/src/mvmnda/rawdata/code \
		${FQDN_IMAGE} \
		/bin/bash



# Build data analysis container
#.PHONY: oci-image-debug
#oci-image:
#	$(OCI_BINARY) build . $(DISTFILE_CACHE_CMD) \
#		-it \
#		-f Containerfile \
#		-t ${FQDN_IMAGE}

# Build data analysis container
.PHONY: oci-image
oci-image:
	$(OCI_BINARY) build . $(DISTFILE_CACHE_CMD) \
		-f Containerfile \
		-t ${FQDN_IMAGE}

# Push containers
.PHONY: oci-push
oci-push:
	$(OCI_BINARY) push ${FQDN_IMAGE}

# Push containers
.PHONY: clean
clean:
	@rm -rf ABI-connectivity-data*


