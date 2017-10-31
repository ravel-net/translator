# Pyretic Simple Static Policy Translation Template

## Intermediate Translation Table _Packet_

Use an intermediate table _Packet_ (This table could also be a view of ravel's base tables.) to map basic fields of a packet that a pyretic policy manipulate on.

Basic fields: _srcip, dstip, srcmac, dstmac, srcport, dstport, forwarding port..._

## Basic Pyretic Policies' Constrains and Updates Over _Packet_

### _match(f<sub>1</sub> = v<sub>1</sub>, f<sub>2</sub> = v<sub>2</sub>, ... , f<sub>n</sub> = v<sub>n</sub>)_

Constrain: match fields f<sub>1</sub>, f<sub>2</sub>, ..., f<sub>n</sub>.<br />
Update: delete unmatched from _Packet_

### _drop_

Constrain: none<br />
Update: truncate _Packet_

### _identity_

Constrain: none<br />
Update: none

### _modify(f<sub>1</sub> = v'<sub>1</sub>, f<sub>2</sub> = v'<sub>2</sub>, ... , f<sub>n</sub> = v'<sub>n</sub>)_

Constrain: _Packet_ is  empty<br />
Update: set f<sub>i</sub> to v'<sub>i</sub> for all entries

### _forward(a)_

Constrain: _Packet_ is empty<br />
Update: set output port to a for all entries

### _flood()_

Constrain: _Packet_ is empty<br />
Update: set output port to FLOOD for all entries

## Translation Procedure

### Definition

1. **basic policy chain**

    A basic policy chain is a policy that contains only pyretic basic policies , parenthesis, forwarding sign(>>) and parallel sign.

2. **necessary parenthesis**

    A pair of parenthesis is said to be necessary if there is at least one parallel sign that is no within its inner parenthesis pairs.

3. **policy scope**

    A policy scope starts at a necessary left parenthesis or a parallel sign and ends at a parallel sign or a necessary right parenthesis. A necessary parenthesis or a parallel sign marks one and only one policy scope's left boundary or/and one policy scope's right boundary.

### Steps

1. For each new entry inserted into rm table, construct _Packet_ table and invoke pyretic policy.

2. Expand the policy to a basic policy chain by replacing _if\_(match(**C**), **P<sub>p<sub />**, **P<sub>n<sub />**)_ with _match(**C**) >> **P<sub>p<sub />** + ~match(**C**) >> **P<sub>n<sub />**_, where _**C**_ is the matching condition and _**P<sub>p<sub />**_ is the positively matched policy and _**P<sub>n<sub />**_ is the negatively matched policy.

3. Strip off unnecessary parenthesis.

4. Execute each module of current policy scope in sequential order.

5. Whenever descend to a child policy scope, create a temporary _Packet_ table for child policy scope that inherited from current policy scope.

6. Whenever elevate to a parent policy scope, union the _Packet_ tables of all its children scopes.

7. Compare each entry in _Packet_ table, map its changes compared to the original entry in _Packet_ table back to ravel's command. Currently available mappings:<br />
    * Changes in switch field -> a new entry in rm table requesting path from OLD.switch to NEW.switch.
    * Changes in output port -> a new entry in cf table building a path from NEW.switch to the switch or host that linked to NEW.output port.