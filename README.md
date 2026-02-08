# ELEC374 MiniSRC Assembler

## Try it out!

A web version is hosted on the Sci '65 server and is available at [src-asm.howdoesthieven.work](https://src-asm.howdoesthiseven.work).

## Overview
The ELEC374 MiniSRC Assembler is a Python tool designed to translate assembly code written for the Mini SRC (a simple 32-bit RISC computer) into a hexadecimal dump of encoded instructions. The output is formatted for use with ModelSim’s $readmemh directive to load instructions into memory.

This assembler supports the following instructions:


- Register register to register (e.g., `add`, `sub`, `and`, `or`, `ror`, `rol`, `shr`, `shra`, `shl`)
- Register to register with constant immediate (e.g., `addi`, `andi`, `ori`)
- Branch instructions with labels (e.g., `brzr`, `brnz`, `brpl`, `brmi`)
- Load/store instructions with offset addressing (e.g., `ld`, `ldi`, `st`)
- Two-register operations (e.g., `mul`, `div`, `not`, `neg`)
- Single-register instructions (e.g., `jal`, `jr`, `in`, `out`, `mflo`, `mfhi`)
- No-argument instructions (e.g., `nop`, `halt`)

It supports labels anywhere you would use a constant. Branch offsets are automatically calculated when using labels, but branch instructions also support constant values.

It also supports these assembler directives:
- `org <const value>`: Sets the current address for subsequent code
- `word <const value>`: Puts a specific constant value in memory at the current memory address 

Two output formats are supported:
- `mem` format: For using ModelSim and the `$readmemh` function
- `mif` format: For use with Quartus

It works by performing two passes:

1. **First Pass:** Extracts labels and assigns instruction addresses (also handles org assembler directive).

2. **Second Pass:** Encodes each instruction into its 32-bit machine code representation. (also handles the word directive)
## Usage
### Prerequisites
- Python 3.6 or later.
- A text editor to write your assembly code.
- The assembly code should follow the syntax as described in the Mini SRC ISA specification.
### Running the Assembler
Open a terminal or command prompt and run the assembler with the following syntax:

```bash
python SRC-ASM.py <input_filename> -o <output_filename> [-v]
```

### Parameters:

- `<input_filename>`: The path to your assembly source file.
- `-o` or `--output`: The path for the output hex file. If omitted, the output file name will be derived from the input file name (with a .mem extension).
- `-v` or `--verbose`: Optional flag. When enabled, the assembler prints the encoded instruction (with addresses) to the console.
## Example
Assume you have an assembly file named `program.s`. To assemble this file and output the hex dump to `output.txt`, run:

```bash
python SRC-ASM.py program.s -o output.txt -v
```
If the `-o` option is omitted, the assembler will create an output file named `program.mem`.

## Output Format
The output file will contain 512 lines (one for each memory word from address 0 to 511) with each line displaying an 8-digit hexadecimal number representing the encoded 32-bit instruction or data. Unused memory locations will be filled with 00000000.

## Error Handling
**Invalid Instructions:** If an instruction or register is not recognized, the assembler will throw an error with details on the parsing failure.

**Memory Range:** The assembler checks that the highest address used does not exceed the available memory (512 words). If it does, an error is reported.

**Verbose Mode:** When running with -v, detailed traceback information is printed for easier debugging.

# Deploying the website

## Running locally

The website can be run locally by running the `app.py` script
```bash
python app.py
```
You should get output looking like this:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 145-628-310
```
Click on the link in the `Running on http://127.0.0.1:5000` line and the server should run. This setup is best for development.

## Running website locally with docker-compose
You can deploy with docker compose by simply running this command:
```bash
docker compose up
```
You can then go to [http://localhost:8080](localhost:8080) and access the website.

## Deploying website on Kubernetes
The current website is deployed using this method. I am using cloudflare tunnels to expose the container to the open internet and for TLS with microk8s on a machine running Ubuntu Server. You can use my commands to achieve the same setup but it requires:
* Cloudflare account
* Docker Hub account
* Domain
* Server running K8s

The deployment yaml files used are in the k8s folder of the repo. The steps below can be used to recreate the deployment setup for this repo. 
1. First create a repo called src-asm on docker hub and set it to private. Then run these commands to build the image and push 
    ```bash
    docker build -t <your docker username>/src-asm:latest . 
    docker push <your docker username>/src-asm:latest
    ```
2. Then, go to cloudflare and create a new tunnel. Choose docker as deployment method, copy the command into a text editor and save the token argument somewhere as it will be used later.

3. Create a k8s namespace:
    ```bash
    kubectl create namespace srcasm
    ```
4. Then generate the cloudflare tunnel token and private docker registry secrets, pasting in the cloudflared token from earlier:
    ```bash
    kubectl create secret docker-registry docker-hub-secret \
    --docker-server=https://index.docker.io/v1/ \
    --docker-username=<docker username> \
    --docker-password='<docker password>' \
    --docker-email=<docker email> -n srcasm
    kubectl create secret generic cloudflared-secret \
    --from-literal=token=<cloudflared token> -n srcasm
    ```
5. Apply the deployments
    ```bash
    kubectl apply -f k8s/cloudflared.yaml -n srcasm
    kubectl apply -f k8s/src-asm-server.yaml -n srcasm
    ```
6. Now the cloudflare tunnel dashboard should say the tunnel is healthy. To enable access to the service, add a public hostname, set the subdomain name, set the service type to http and set the url to `src-asm-server:8080`.

Now you can access the service at the public hostname created with TLS enabled.

## Deploying website with docker-compose 
If you want to also deploy it with cloudflare tunnels, you can create a `cloudflare-tunnel-secret.yaml` file and add this to the file, replacing \<token\> with your cloudflare tunnel token
```
TUNNEL_TOKEN=<token>
```
In your tunnel, set the service type to `http` and set the url to `src-asm:5000`.
Then run the command below:
```bash
docker compose --profile staging up
```
Instructions for how to get the cloudflare token are in the Kubernetes section. 


# Contact
For questions, bug reports, or feature requests, please contact:
asmhelp@davlaf.com
