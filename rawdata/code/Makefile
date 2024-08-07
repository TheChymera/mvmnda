# We must allow others exactly use our script without modification
# Or its not replicable by others.
#
REGISTRY=docker.io
REPOSITORY=centerforopenneuroscience

IMAGE_NAME=mvmnda

# Allow changing this on invocation by setting the variable
#IMAGE_TAG=0.0.3
IMAGE_TAG=latest

FQDN_IMAGE=${REGISTRY}/${REPOSITORY}/${IMAGE_NAME}

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
	mkdir -p ${SCRATCH_PATH}
	SCRATCH_PATH=${SCRATCH_PATH} python -c "import reposit; reposit.convert_all(\"${IN_DIR}\")"


.PHONY: bids-dandi
bids-dandi:
	cd ${SCRATCH_PATH}; dandi organize -d ${OUT_PATH} .


.PHONY: bids
bids:
	( \
	cd nwb2bids; \
	mkdir -p .venv; \
	python -m venv .venv/; \
	source .venv/bin/activate; pip install -e . ; \
	python -c "from nwb2bids import reformat; reformat.reformat_all(\"${SCRATCH_PATH}\", \"${OUT_PATH}\")" ; \
	)

.PHONY: data
data: nwb


.PHONY: data-singularity
data-singularity:
	cd ../../
	singularity run --cleanenv --no-home -W $$PWD -B $$PWD:$$PWD .datalad/environments/mvmnda/image make -C rawdata/code/ data

# DISCLAIMER: not tested.  Needs 
update-singularity:
	cd ../../
	datalad containers-add --url docker://centerforopenneuroscience/mvmnda:??? --update mvmnda 

.PHONY: data-oci
data-oci:
	$(OCI_BINARY) run \
		-it \
		--rm \
		-v ${PWD}/../..:/root/src/mvmnda \
		-v ~/.local/share/mvmnda/nwbdata/:~/.local/share/mvmnda/nwbdata/ \
		--workdir /root/src/mvmnda/rawdata/code \
		${FQDN_IMAGE}:${IMAGE_TAG} \
		make data

.PHONY: data-oci-interactive
data-oci-interactive:
	$(OCI_BINARY) run \
		-it \
		--rm \
		-v ${PWD}/../..:/root/src/mvmnda \
		-v ~/.local/share/mvmnda/nwbdata/:/root/.local/share/mvmnda/nwbdata/ \
		--workdir /root/src/mvmnda/rawdata/code \
		${FQDN_IMAGE} \
		/bin/bash


.PHONY: oci-image
oci-image:
	$(OCI_BINARY) build . $(DISTFILE_CACHE_CMD) \
		-f Containerfile \
		-t ${FQDN_IMAGE}:${IMAGE_TAG} \
		-t ${FQDN_IMAGE}:latest

.PHONY: oci-push
oci-push:
	$(OCI_BINARY) push ${FQDN_IMAGE}:${IMAGE_TAG} 
	$(OCI_BINARY) push ${FQDN_IMAGE}:latest


.PHONY: clean
clean:
	rm -rf ${SCRATCH_PATH}
