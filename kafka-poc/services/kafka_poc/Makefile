# Go parameters
GOCMD=go
GOGET=$(GOCMD) get
PROTOCCMD=protoc
PROTODIR=./protos
OUTDIR=./messages
PROTO=./protos/hello.proto

all: build

build:
	mkdir -p $(OUTDIR)
	$(PROTOCCMD) -I=$(PROTODIR) --go_out=$(OUTDIR) $(PROTO)

deps:
	$(GOGET) -u github.com/golang/protobuf/protoc-gen-go
