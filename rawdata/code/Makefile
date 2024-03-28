# We must allow others exactly use our script without modification
# Or its not replicable by others.
#
REGISTRY=docker.io
REPOSITORY=centerforopenneuroscience

IMAGE_NAME=mvmnda
IMAGE_TAG=0.0.2

FQDN_IMAGE=${REGISTRY}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}

OCI_BINARY?=podman
PACKAGE_NAME=mvmnda
RELEASE_VERSION?=9999
RESOLUTION?=9999 # specified in microns
SCRATCH_PATH?=~/.local/share/mvmnda/nwbdata/
IN_DIR?=../../sourcedata/

OUT_PATH=$(PWD)/../

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

.PHONY: nwb
nwb:
	SCRATCH_PATH=${SCRATCH_PATH} python -c "import reposit; reposit.convert_all(\"${IN_DIR}\")"


.PHONY: bids-dandi
bids-dandi:
	cd ${SCRATCH_PATH}; dandi organize -d ${OUT_PATH} .


.PHONY: bids
bids:
	python -c "from nwb2bids import reformat; reformat.reformat_all(\"${SCRATCH_PATH}\", \"${OUT_PATH}\")"

.PHONY: data
data: nwb


.PHONY: data-oci
data-oci:
	$(OCI_BINARY) run \
		-it \
		--rm \
		-v ${PWD}/../..:/root/src/mvmnda \
		--workdir /root/src/mvmnda/rawdata/code \
		${FQDN_IMAGE} \
		make data

.PHONY: data-oci-interactive
data-oci-interactive:
	$(OCI_BINARY) run \
		-it \
		--rm \
		-v ${PWD}/../..:/root/src/mvmnda \
		--workdir /root/src/mvmnda/rawdata/code \
		${FQDN_IMAGE} \
		/bin/bash


.PHONY: oci-image
oci-image:
	$(OCI_BINARY) build . $(DISTFILE_CACHE_CMD) \
		-f Containerfile \
		-t ${FQDN_IMAGE}

.PHONY: oci-push
oci-push:
	$(OCI_BINARY) push ${FQDN_IMAGE}


.PHONY: clean
clean:
	rm -rf ${SCRATCH_PATH}
