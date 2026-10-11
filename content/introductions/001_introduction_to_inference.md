# Introduction

Large language models (LLMs) are increasingly used across diverse domains, ranging from technical to creative work. In software engineering, these models have shown practical value in generating code and accelerating software development.

The process by which a model generates outputs from an input is known as **inference**. Inputs and outputs are typically expressed as tokens, which are units of text the model uses to interpret and generate language.

As LLM usage grows, inference becomes not only a model-performance problem but also an infrastructure and economics problem. An inference provider must determine how quickly requests should be served, how much work the system can process, how much infrastructure is required, and ultimately how much it costs to perform inference.

The fastest possible system is not necessarily the most economical system. Likewise, an optimization that makes a model run faster does not necessarily reduce the cost of serving it.

The objective of inference optimization is therefore not simply to maximize performance. It is to provide the level of performance required by an application while using the available infrastructure as efficiently and economically as possible.

This article develops that idea progressively. It examines the metrics that define inference performance and cost, why those metrics trade off against one another, how workload and demand change the operating conditions of the system, how application requirements define the required performance target, when performance improvements actually become cost savings, and where optimization can occur across the inference stack.

---
# The Metrics That Define Inference Performance and Cost

Inference requests are executed by a model running on hardware resources such as GPUs in data centers. The requests are handled by inference providers, which may provide access to proprietary models or host open-source or open-weight models.

From the user's perspective, the most visible concerns are straightforward:

- How quickly will the first token arrive?
- How long will the request take to complete?
- How much does the inference cost?

From the provider's perspective, these same questions become infrastructure questions:

- How much work can the system process per unit of time?
- What hardware is required, and how much of it is needed?
- How efficiently are the infrastructure's hardware resources being utilized?
- What is the infrastructure cost per unit of inference?

At a high level, three quantities capture much of this problem: **latency, throughput, and serving cost**.

Fig 1. Inference metrics

**Latency** describes how long the system takes to respond to and complete an inference request.

Latency can be measured at different stages. A user may care about how long the inference request takes before the first token appears, how quickly subsequent tokens are generated, or how long the entire request takes to complete.

A request containing a long document may take longer to begin generating a response than a simple question because the model must process substantially more input before generation begins.

For an interactive application, lower latency generally produces a more responsive user experience.

**Throughput** describes how much work the system can process per unit of time.

Depending on the context, throughput may be measured in tokens per second, requests per second, or another measure of completed work.

A system handling only a single request may use only part of the hardware's available capacity. When multiple requests are processed concurrently, the system can often improve hardware utilization and process more useful work using the same infrastructure.

Higher throughput therefore allows the infrastructure to serve more inference over the same period of time.

**Serving cost** describes the infrastructure cost required to perform inference. It is typically normalized by the amount of inference served, such as cost per token, cost per million tokens, or cost per request.

Latency and throughput influence serving cost, but neither determines it independently.

Higher throughput can distribute the same infrastructure cost across more tokens. Optimizations that reduce the resources or execution time required per request can also increase serving capacity. Whether these performance improvements translate into lower serving cost depends on workload, demand, and infrastructure provisioning.

---
# The Tradeoffs of Inference Optimization

An ideal inference system would minimize latency and serving cost while maximizing throughput. In practice, these objectives are not always simultaneously achievable. Improvements along one dimension may require accepting degradation along another.

If the objective is to minimize the latency of an individual request, the system can begin processing the request as soon as sufficient resources become available. This reduces queueing delay and improves responsiveness, but may result in low hardware utilization when only a small number of requests are active. As the number of concurrent requests increases, the system can execute more requests simultaneously by grouping them into batches, generally increasing hardware utilization and aggregate throughput.

A useful analogy to compare these tradeoffs is a car and a bus. A single car can transport a passenger to the destination quickly. But reusing the same car among many waiting passengers, or maintaining a one-to-one ratio of passengers to cars, is inefficient in either time or cost. A passenger at the end of the queue may wait a long time, while providing a separate car for every passenger is expensive. A bus instead can batch multiple passengers into a single trip, using one vehicle more efficiently at the cost of some individual passengers waiting longer before departure. Under high demand, this can reduce the time by which nearly all passengers have reached their destination. Inference batching exhibits the same tradeoff: individual execution favors per-request latency, whereas batching improves aggregate throughput and can reduce tail completion time under high load.

Fig 2. Car bus analogy

With limited infrastructure capacity, requests increasingly contend for available resources as the offered load approaches the maximum serving capacity of the system. Queueing delays consequently increase, and latency may rise sharply as demand approaches or exceeds sustainable throughput. This creates a tug of war between latency and throughput: operating at higher utilization can improve aggregate throughput, while maintaining lower latency may require preserving excess capacity.

This dependence on operating conditions is closely related to the broader principle expressed by the No Free Lunch Theorem: no single optimization strategy is universally superior across all possible problem settings. In inference systems, an optimization that provides substantial benefit under one workload, traffic pattern, or infrastructure configuration may provide little benefit under another.
The appropriate operating point therefore depends on the conditions under which the system is expected to function: the characteristics of the inference requests and the manner in which those requests arrive over time.

---

# Why Identical Inference Systems Can Produce Different Inference Metrics

Two inference systems using the same model, hardware configuration, and inference optimizations can nevertheless exhibit different latency, throughput, and serving cost. System behavior depends not only on how the system is constructed, but also on the characteristics of the requests it receives and the rate at which those requests arrive.

Two quantities capture much of this variation: workload and demand.

Fig 2 image od different wwor;oad and demand

## Workload

Workload describes the computational characteristics of the requests presented to the system. Relevant variables include input length, output length, and other request properties that determine computation, memory consumption, and data movement. Processing many input tokens permits substantial parallel computation and typically places greater demand on compute throughput. Output generation, by contrast, proceeds sequentially and repeatedly accesses model parameters and request-specific state, making performance more sensitive to memory bandwidth. Consequently, longer inputs generally increase computational demand, whereas longer outputs increase the volume of sequential, memory-bandwidth-intensive processing.

Workload characteristics therefore determine both the magnitude and composition of the resources required for inference and influence which system optimizations are effective.

## Demand

Demand describes the volume of inference work presented to the system and its distribution over time.

Relevant variables include request arrival rate, concurrency, burstiness, and temporal variation in traffic.

At low demand, only a small number of requests may be active, leaving part of the available hardware capacity unused. As demand increases, greater concurrency can improve hardware utilization and aggregate throughput. As demand approaches the serving capacity of the system, however, requests begin to queue for finite execution resources. The resulting queueing delay increases end-to-end latency and can become a dominant component of request completion time under sustained high load.

Workload and demand therefore describe distinct but complementary dimensions of inference. Workload determines the resource requirements of individual requests, whereas demand determines the temporal pressure placed on those resources. Their interaction governs utilization, queueing, and resource contention, and ultimately determines the latency, throughput, and serving cost observed in practice.

---
# How SLA and Application Requirements Define the Target Metrics

There is no universally optimal configuration for LLM inference. The appropriate operating point is determined by the requirements of the application, which specify which dimensions of performance are relevant and the constraints within which the system must operate.

These requirements vary substantially across applications. An offline workload processing a large dataset may tolerate high per-request latency provided that the complete workload finishes within a specified time window. In this setting, aggregate throughput and infrastructure cost may dominate the optimization objective. Interactive applications impose different constraints. A conversational assistant must begin generating output sufficiently quickly to maintain responsiveness, whereas real-time voice applications impose tighter latency requirements because delays directly disrupt the continuity of interaction.

These requirements are typically expressed as service-level objectives (SLOs) and may be formalized within a Service Level Agreement (SLA). Depending on the application, they may constrain latency, availability, reliability, throughput, completion time, or other application-specific measures of service quality.

The optimization objective is therefore not to maximize performance in isolation, but to satisfy the required service level at the lowest practical infrastructure cost. The resources required to do so depend jointly on workload and demand: workload determines the computation, memory, and communication required by individual requests, whereas demand determines the volume and temporal distribution of those requests. Consequently, systems subject to the same service-level requirements may require substantially different infrastructure configurations when operating under different workloads or demand patterns.

Inference optimization can therefore be formulated as the alignment of application requirements, workload, demand, and infrastructure. Application requirements define the performance constraints; workload and demand determine the computational burden imposed on the system; and infrastructure provides the resources required to satisfy that burden. The objective is to identify an operating configuration that satisfies the required service level with the minimum economically practical infrastructure expenditure.

---

# Better Performance Does Not Necessarily Mean Lower Cost

Improvements in latency or throughput can create opportunities to reduce inference cost, but performance gains do not necessarily translate into economic gains.

Consider an optimization that doubles the amount of inference a fixed hardware configuration can process per unit time. The optimization increases the system's serving capacity, but the economic value of that capacity depends on whether it can be productively used.

Under sufficient demand, the same infrastructure can process more requests or tokens over a given period, distributing its cost across a larger volume of useful inference and thereby reducing cost per unit. When demand remains below capacity, however, the additional capacity may remain unused. Requests may complete faster, but if the same infrastructure remains provisioned and the volume of useful inference is unchanged, the cost per unit may remain largely unchanged.


Performance improvements can therefore reduce cost through two principal mechanisms: increasing the amount of useful inference served by a fixed quantity of infrastructure, or reducing the infrastructure required to serve a fixed amount of inference. In either case, the performance gain must ultimately translate into greater productive utilization or lower infrastructure expenditure.

This distinction is important when interpreting inference benchmarks. A twofold increase in tokens processed per second represents a performance improvement, but does not by itself imply a twofold reduction in production serving cost. The economic effect depends on workload, demand, service-level requirements, infrastructure configuration, and whether the additional capacity can be consumed or removed.

The optimization objective is therefore:
> Provide the required service level for the actual workload and demand using the minimum economically practical infrastructure.

---

# Winning in Inference is not always dictated by who has the best hardware

Hardware defines the resource envelope within which inference operates, including available compute throughput, memory capacity, memory bandwidth, and interconnect performance. More capable accelerators can expand this envelope, but hardware alone does not determine either system performance or economic efficiency.

Newer accelerators may also carry higher capital costs in owned infrastructure or higher operating costs in rented environments. The highest-performing hardware is therefore not necessarily the most economical choice for every workload. Offline processing may satisfy its completion-time requirements on less expensive accelerators, whereas latency-sensitive applications may require substantially greater hardware capability to meet their service-level objectives.
Hardware selection must consequently be evaluated in the context of the workload and its performance requirements. Once a platform is selected, efficiency depends on how effectively its compute, memory, and communication resources are utilized.

This distinction is particularly important in LLM inference because resource requirements vary across models and stages of execution. Model architecture influences computation, memory consumption, and communication, while input processing and sequential output generation exhibit different computational and memory-access characteristics. The same hardware can therefore exhibit substantially different performance depending on the workload and the software mechanisms used to execute it.

Substantial gains in inference efficiency can consequently be achieved without replacing the underlying hardware. Improvements may instead arise from changes to model representation, inference algorithms, execution engines, accelerator software, distributed execution, or system orchestration. Together, these components constitute the inference stack.

---

# The Inference Stack

The inference system can be decomposed into seven interacting layers that span the path from the mathematical structure of a model to its operation as a production service. Each layer exposes a different optimization surface, while the performance of the complete system emerges from their interaction. Any inference optimization will fall under one of the seven categories.

## 1. Model Architecture & Representation

The model defines the fundamental computation required during inference. Relevant properties include parameter count, attention architecture, mixture-of-experts structure, model dimensions, KV-cache characteristics, and numerical representation.

These properties establish much of the compute, memory, and communication demand before additional serving optimizations are introduced. Architectural changes can therefore alter not only the number of operations required during inference but also memory capacity requirements, data movement, and communication between devices.

## 2. Inference Optimization Algorithms

Inference algorithms modify how the computation defined by the model is executed. Their objective is typically to reduce computation, memory consumption, memory movement, or the number of sequential decoding operations required to generate output.

Representative techniques include quantization, optimized attention algorithms, speculative decoding, and sparsity-based methods. These approaches can substantially alter the resource requirements of inference while preserving, to varying degrees, the application-visible behavior of the underlying model.

## 3. Inference Engine & Scheduling

The inference engine determines how requests are executed and how hardware resources are shared over time. Systems such as vLLM, SGLang, and TensorRT-LLM manage request scheduling, batching, KV-cache allocation, memory management, caching, concurrency, and request execution.

This layer is central to production inference because requests rarely execute in isolation. The engine determines how individual workloads are multiplexed onto finite hardware resources and therefore directly influences utilization, latency, throughput, and serving capacity.

## 4. Accelerator Software Stack

The accelerator software stack translates model operations into instructions that can be executed efficiently by the underlying hardware. It includes compilers and intermediate representations, kernel implementations, mathematical and tensor libraries, communication libraries, runtimes, and drivers.

The efficiency of this translation can significantly affect realized hardware performance. Identical mathematical operations may exhibit substantially different execution characteristics depending on how effectively implementations use compute units, registers, cache hierarchies, accelerator memory, and memory bandwidth.

## 5. Compute, Memory & Interconnect Hardware

Hardware provides the physical resources on which inference executes. These resources include accelerators, accelerator memory, memory bandwidth, CPUs, device-to-device interconnects, and machine-to-machine networking.

Different inference operations can be constrained by different components of this hardware. Some operations are predominantly compute-limited, whereas others are limited by memory capacity or by the rate at which model weights and KV-cache data can be transferred. Distributed execution introduces an additional dependence on communication bandwidth and latency between accelerators and machines.

Hardware selection therefore requires identifying which resources constrain the relevant workload rather than considering accelerator performance as a single scalar quantity.

## 6. Distributed Inference and Disaggregated Serving

When the requirements of a model or workload exceed the resources available on a single accelerator, computation must be distributed across multiple devices or machines.

Common approaches include tensor parallelism, pipeline parallelism, expert parallelism, data parallelism, and prefill-decode disaggregation. Each partitions computation or serving responsibilities differently and therefore creates a distinct pattern of memory use, synchronization, and communication.

The effectiveness of a distributed configuration depends jointly on model structure, accelerator memory, interconnect performance, communication software, workload characteristics, and deployment scale. Distribution can increase the resources available to inference, but it also introduces communication overheads that may themselves become limiting factors.

## 7. Inference Orchestration & Operations

At production scale, individual inference workers must be coordinated into a service capable of operating under changing demand and partial system failure. The orchestration layer manages worker placement, replica management, traffic routing, autoscaling, resource allocation, deployment, failure recovery, and coordination across inference workers.

Whereas the inference engine manages execution within a worker or group of tightly coupled workers, orchestration determines how those workers collectively form an elastic and reliable production system.

---

The layers of the inference stack are not independent. A model architecture can alter KV-cache requirements, which in turn affect engine scheduling, memory consumption, hardware selection, and distributed execution. A distributed serving strategy depends on both communication libraries and the physical interconnect beneath them. Similarly, an optimization implemented by an inference engine may provide substantial benefit for one workload while remaining largely irrelevant for another.

Workload, demand, and measurement therefore cut across the entire stack. Workload determines the computational characteristics of the requests presented to the system. Demand determines the amount and temporal distribution of that work. Measurement determines whether modifications to the stack produce the intended application-level and economic outcomes.

The stack thus represents the **optimization surface** of an inference system: it identifies where changes can be introduced, but not which changes will be beneficial. Determining that requires measurement under the workload and demand conditions that the system is actually expected to serve.

---

# From Optimization to System-Level Improvement
An optimization has practical value only if it improves an application-relevant outcome or reduces the resources required to achieve that outcome.

Evaluation therefore begins by measuring the existing system under representative workload and demand conditions. This establishes a baseline from which the dominant constraint can be identified. Depending on the system, the limiting factor may arise from compute throughput, memory bandwidth,  communication, scheduling, hardware utilization, provisioning, or another component of the inference stack.

A targeted modification can then be introduced at the appropriate layer and evaluated against the required service level. Relevant measures include application-visible latency, throughput, infrastructure utilization, resource requirements, and serving cost. An improvement in an isolated benchmark is insufficient if it does not translate into better service-level performance, greater productive capacity, or lower infrastructure requirements.

Inference optimization is therefore fundamentally a systems problem. Changes at one layer can alter the operating conditions of others, and removing one bottleneck may expose another. The relevant constraint is consequently not fixed: it depends on the workload, demand, infrastructure, and service-level requirements under which the system operates.

Optimization therefore proceeds iteratively: characterize the workload and demand, define the required service level, measure the system, identify the dominant constraint, introduce an appropriate intervention, and measure the resulting system-level effect. This process repeats as workloads, demand, infrastructure, and application requirements evolve.

The central question in inference optimization is therefore not simply, “How fast can this system run?” but rather, “What constrains the system from meeting its service-level requirements, and what intervention can satisfy those requirements at the lowest practical cost?”
This leads to the central principle of LLM inference optimization:
> The objective is not maximum performance in isolation. It is the performance required by the application, for the actual workload and demand, achieved at the lowest economically practical infrastructure cost.

---
## LLM-Compendium 

This website will now dive into the technical details of LLM inference, dissecting each of the seven layers of the inference stack and developing an understanding of inference from first principles. Both theoretical back-of-the-envelope calculations and representative coding examples are provided. The purpose is to understand LLM inference from first principles and in the context of its underlying objectives.