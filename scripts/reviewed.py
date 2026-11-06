"""Human/model-reviewed mappings from complete paper texts; no keyword inference.

One offered question is counted once. Mixed chapter questions retain their full
marks as a joint bucket when the paper does not print a per-part mark allocation.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P={1:'Rotational Dynamics',2:'Mechanical Properties of Fluids',3:'Kinetic Theory of Gases and Radiation',4:'Thermodynamics',5:'Oscillations',6:'Superposition of Waves',7:'Wave Optics',8:'Electrostatics',9:'Current Electricity',10:'Magnetic Fields due to Electric Current',11:'Magnetic Materials',12:'Electromagnetic Induction',13:'AC Circuits',14:'Dual Nature of Radiation and Matter',15:'Structure of Atoms and Nuclei',16:'Semiconductor Devices'}
M={1:'Mathematical Logic',2:'Matrices',3:'Trigonometric Functions',4:'Pair of Straight Lines',5:'Vectors',6:'Line and Plane',7:'Linear Programming',8:'Differentiation',9:'Applications of Derivatives',10:'Indefinite Integration',11:'Definite Integration',12:'Applications of Definite Integration',13:'Differential Equations',14:'Probability Distributions',15:'Binomial Distribution'}
C={1:'Solid State',2:'Solutions',3:'Ionic Equilibria',4:'Chemical Thermodynamics',5:'Electrochemistry',6:'Chemical Kinetics',7:'Elements of Groups 16, 17 and 18',8:'Transition and Inner Transition Elements',9:'Coordination Compounds',10:'Halogen Derivatives',11:'Alcohols, Phenols and Ethers',12:'Aldehydes, Ketones and Carboxylic Acids',13:'Amines',14:'Biomolecules',15:'Introduction to Polymer Chemistry',16:'Green Chemistry and Nanochemistry'}
CS1={1:'Operating System',2:'Data Structure',3:'C++ Programming',4:'HTML'}
CS2={1:'Introduction to Microprocessors and 8085',2:'Instruction Set and Programming of 8085',3:'Introduction to Intel x86 Family',4:'Introduction to Microcontrollers',5:'Networking Technology'}
Q=[];REVIEWS={}
def label(d,k):
    return d[k] if isinstance(k,int) else 'Mixed: '+' / '.join(d[x] for x in k)
def add(paper,q,marks,chapter,topic):
    Q.append(dict(paperId=paper,question=q,marks=marks,chapter=chapter,topic=topic,reviewed=True,allocation='joint' if chapter.startswith('Mixed:') else 'single chapter'))
def pcm(paper,d,mcq,veryshort,rest,expected):
    for i,k in enumerate(mcq,1):add(paper,f'1({i})',2 if d is M else 1,label(d,k),'Multiple-choice item')
    for i,k in enumerate(veryshort,1):add(paper,f'2({i})',1,label(d,k),'Very short answer')
    for n,entry in enumerate(rest,3):
        k,topic=entry;marks=2 if n<=14 else 3 if n<=26 else 4
        add(paper,str(n),marks,label(d,k),topic)
    total=sum(q['marks'] for q in Q if q['paperId']==paper)
    assert total==expected,(paper,total,expected)
    REVIEWS[paper]={'offeredMarks':expected,'maxMarks':80 if d is M else 70,'reviewNote':'All questions mapped. Mixed-chapter questions retain a joint marks bucket; no unprinted subpart marks inferred.'}
def cs(paper,d,keys,topics=None):
    names=[f'1(A)({x})' for x in 'abcd']+[f'1(B)({x})' for x in 'abc']
    marks=[1]*4+[3]*3
    for n in [2,3,4]:names += [f'{n}(A)({x})' for x in 'abc']+[f'{n}(B)({x})' for x in 'ab'];marks += [3]*3+[4]*2
    names += [f'5({choice})({x})' for choice in ['A','B'] for x in 'abc'];marks += [5]*6
    if topics is None:topics=['Reviewed theory item' for _ in range(22)]+['Programming alternative' for _ in range(6)]
    assert len(keys)==len(names)==len(topics),(paper,len(keys),len(names),len(topics))
    for q,mark,k,t in zip(names,marks,keys,topics):add(paper,q,mark,label(d,k),t)
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==94
    REVIEWS[paper]={'offeredMarks':94,'maxMarks':50,'reviewNote':'Includes both mutually exclusive programming alternatives in Q5. Offered marks are 94; maximum attainable marks are 50.'}

pcm('a34aba1683a5',P,[2,3,14,4,1,12,14,5,11,13],[8,9,10,11,7,15,6,5],[
(12,'Eddy currents'),(9,'Meter bridge errors'),(7,'Biprism interference'),(15,'Bohr orbit radius'),(1,'Fan rotational power'),(8,'Dipole work'),(10,'Biot-Savart circular arc'),(16,'Photodiode'),(6,'Harmonics and overtones'),(2,'Viscous drag'),(3,'Gas molecular energy'),(13,'AC inductor'),
(4,'Equilibrium definitions'),(13,'Series resonance'),(11,'Oscillating bar magnet'),(11,'Magnetization and susceptibility'),(8,'Potential of a charge'),(14,'Electron de Broglie wavelength'),(16,'Full-wave rectifier'),(6,'Guitar string frequency'),(4,'Isothermal expansion'),(10,'Galvanometer conversion'),(10,'Coaxial cable field'),(15,'Bohr electron energy'),
(2,'Laplace surface tension law'),(1,'Safe turning speed and moment of inertia'),(3,'Radiation coefficients and molecular speeds'),(12,'Self/mutual induction and induced emf'),(7,'Interference fringe width')],98)
pcm('b8daa39d6a0a',P,[1,2,6,8,10,14,4,12,5,7],[1,2,9,10,15,4,14,8],[
(4,'Heating and internal energy'),(7,'Huygens wavefront'),(11,'Magnetization'),(5,'SHM differential equation'),(10,'Galvanometer to voltmeter'),(10,'Biot-Savart law'),(16,'LED'),(12,'Aircraft motional emf'),(1,'Maximum turning speed'),(2,'Viscosity'),(6,'Tuning fork wavelengths'),(15,'Bohr angular momentum'),
(10,'Circular coil magnetic field'),(14,'Photoelectric experiment'),(16,'Transistor current gains'),(2,'Surface energy'),(4,'Isothermal work'),(6,'Stationary waves'),(13,'LCR impedance'),(15,'Balmer wavelengths'),(11,'Magnetic susceptibility'),(1,'Banked track'),(4,'Mayer relation'),(13,'AC voltage'),
(12,'Transformer'),(7,'Double-slit fringe width'),((9,5),'Meters and SHM energy'),(3,'Black body and molecular speeds'),(8,'Capacitor energy and spherical field')],98)
pcm('6d36de2f222b',M,[1,2,3,6,8,9,11,14],[1,3,10,13],[
(1,'Switching circuit'),(3,'Triangle identity'),(3,'General trigonometric solution'),(4,'Slopes of a pair of lines'),(5,'Perpendicular vectors'),(6,'Vector equation of a line'),(8,'Implicit derivative'),(8,'Derivative'),(9,'Increasing function'),(9,'Related rate of circle area'),(10,'Trigonometric integral'),(15,'Binomial variance'),
(1,'Statement classification'),(3,'Sine rule'),(5,'Centroid coordinates'),(5,'Triangle vector identity'),(6,'Intersecting lines'),(6,'Plane equation'),(8,'Chain rule proof'),(9,'Lagrange mean value theorem'),(10,'Trigonometric integral'),(13,'Separable differential equation'),(14,'Mean and variance'),(15,'Repeated dice trials'),
(2,'Adjoint identity'),(4,'Homogeneous pair of lines'),(5,'Internal section formula'),(7,'Graphical optimization'),(10,'Rational integration'),(11,'Definite integral symmetry'),(12,'Area between circle and line'),(13,'Homogeneous differential equation')],112)
pcm('692739a10298',M,[1,3,5,6,8,11,13,15],[1,5,10,13],[
(1,'Truth table'),(2,'Invertible matrix'),(3,'Triangle trigonometry'),(4,'Slopes of a pair of lines'),(5,'Section ratio'),(6,'Vector equation of a line'),(8,'Logarithmic differentiation'),(10,'Logarithm integral'),(11,'Definite integral'),(12,'Area under curve'),(13,'Substitution in differential equation'),(14,'Coin distribution'),
(1,'Switching table'),(3,'Inverse tangent identity'),(3,'Triangle identity'),(5,'Semicircle vector proof'),(6,'Shortest distance between lines'),(6,'Angle of line and plane'),(8,'Second derivative identity'),(9,'Approximate inverse tangent'),(10,'Indefinite integral identity'),(13,'Differential equation'),(14,'Probability density normalization'),(15,'Six dice trials'),
(2,'Matrix reduction'),(4,'Angle between a pair of lines'),(5,'Parallelepiped volume'),(7,'Graphical optimization'),(8,'Parametric differentiation'),(9,'Box volume optimization'),(10,'Rational integral'),(11,'Definite integral property')],112)
pcm('68d3d8bdd911',C,[5,7,10,2,6,4,9,13,8,3],[7,5,8,11,12,1,15,16],[
(1,'Isomorphism and unit cell'),(7,'Halogen trends'),(9,'Complex ligand types'),((14,10),'Glucose oxidation and enantiomers'),((16,11),'Nanostructure and ether hydrolysis'),(2,'Osmotic pressure'),(4,'First law processes'),(8,'Lanthanoids and actinoids'),(10,'Chlorobenzene substitution'),(12,'Cannizzaro reaction'),(6,'Rate law and intermediate'),(5,'Electrode potential'),
((2,4),'Vapour-pressure derivation and second law'),((13,3),'Amide conversion and amphoteric water'),(11,'Alcohol/phenol/ether conversions'),((14,7),'Peptide bond and interhalogens'),((8,16),'Chromium configuration, magnetic moment and green chemistry'),((9,4),'Biological complexes and expansion work'),((16,12),'Atom economy and organic oxidation'),((15,8),'Nylon-6 and transition-ion colour'),((9,12),'Werner theory and acetone reaction'),((12,13),'Tollens test and diazonium chemistry'),((3,14),'Common ion and glucose preparation'),((12,6),'Hydrazone and rate constant'),
((2,6,4),'Isotonic solution, molecularity and Hess law'),((1,15),'Crystal defect, ferromagnetism and polymers'),((9,5),'Effective atomic number, accumulator and fuel cell'),((12,10),'Acid reduction and alkaline hydrolysis'),((3,7),'Acid dissociation, epsom salt and sulphuric acid')],98)
cs('fe7befff7f7e',CS1,[1,2,3,4,1,2,3,3,2,1,2,1,4,3,2,1,3,1,3,2,3,1,3,3,4,3,3,4],[
'Windows NT','Binary search','Multiple inheritance','Image tag attribute','System calls','Linear and nonlinear structures','C++ data types','Parameter passing','Record representation','OS functions','Array insertion algorithm','Tape and disk file systems','HTML formatting tags','Scope resolution','Structure operations','Disk terms','Operator overloading','Linux features','OOP features','Expression binary tree','Inheritance diagrams','Memory partitioning','Factorial program','Array sum program','HTML result table','Integer reverse program','Class-based area program','HTML definition list'])
cs('60b2d4536525',CS2,[1,2,4,5,1,4,3,1,1,4,2,3,2,2,5,1,5,5,5,1,5,2,2,2,2,2,2,2],[
'ALE pin','INR flag effects','8051 feature','Network protocol','Interrupt types','Microcontroller applications','Pentium attributes','8085 pins','CPU functions','8051 features','DAA instruction','Pentium programming model','8085 addressing modes','Branch instructions','Wireless medium','Timing cycles','Hub types','Fibre and coaxial media','Transmission characteristics','8085 programming model','Ring topology','Instruction trace','Multiply bytes','Exchange blocks','Separate nibbles','Add multibyte numbers','Fill alternating bytes','Find block minimum'])

pcm('69070f9d4378',P,[4,13,8,7,3,10,1,2,7,6],[9,2,14,16,5,15,12,1],[
(1,'Moment of inertia'),(8,'Dielectrics'),(4,'Thermodynamic processes'),(15,'Bohr orbit radius'),(6,'Harmonics and overtones'),(9,'Potentiometer versus voltmeter'),(4,'Mechanical and thermal equilibrium'),(15,'Orbital electron angular momentum'),(7,'Double-slit fringes'),(2,'Coalescing droplets'),(13,'Resonant frequency'),(4,'Specific heats'),
(7,'Reflection wavefront'),(11,'Magnetization and susceptibility'),(6,'Beat frequency'),(13,'Reactance and impedance'),(1,'Rotational kinetic energy'),(12,'Motional emf'),(2,'Terminal velocity'),(15,'Spectral series limits'),(10,'Straight-wire field'),(8,'Parallel-plate capacitance'),(12,'Mutual induction'),(9,'Parallel cells'),
(3,'Kinetic gas pressure'),(16,'Half-wave rectifier'),((10,4),'Galvanometer diagram and compression work'),(5,'Seconds pendulum and SHM period'),(14,'Matter wavelength and work function')],98)
pcm('101c8e160901',P,[3,4,16,7,12,2,16,11,14,15],[9,10,13,14,1,8,5,11],[
(2,'Viscosity coefficient'),(10,'Toroid field'),(1,'Angular momentum conservation'),(8,'Series capacitance'),(12,'Parallel inductors'),(10,'Galvanometer to ammeter'),(13,'AC resistor'),(11,'Oscillating bar magnet'),(5,'Free and forced vibrations'),(3,'Radiative heat loss'),(4,'Adiabatic compression'),(15,'Decay constant'),
(7,'Huygens reflection'),(15,'Bohr postulates'),(11,'Magnetization and susceptibility'),(14,'Photoelectric experiment'),(9,'Potentiometer cell resistance'),(16,'Common-base transistor'),(5,'SHM acceleration and velocity'),(6,'Tuning fork wavelength'),(7,'Biprism wavelength'),(10,'Parallel-wire force'),(13,'AC frequency and current'),(8,'Electric dipole torque and work'),
(3,'Kinetic gas pressure'),(12,'Inductor energy and falling-wire emf'),(4,'Isothermal work and first law'),(2,'Surface energy and soap bubble'),(1,'Vertical circular motion')],98)
pcm('dd76c75b9a74',P,[4,2,3,8,9,14,16,1,6,12],[2,12,10,4,11,1,8,3],[
(6,'Harmonics and overtones'),(2,'Newton viscosity law'),(10,'Circular arc field'),(1,'Angular momentum conservation'),(16,'LED advantages'),(3,'Black-body radiation'),(12,'Mutual inductance'),(13,'LCR phase'),(9,'Potentiometer advantages'),(16,'Full-wave circuit'),(5,'SHM force and period'),(4,'Isothermal work'),
(11,'Oscillating bar magnet'),(4,'Equilibrium definitions'),(7,'Brewster angle'),(15,'Radioactive decay'),(3,'Kirchhoff radiation law'),(6,'Pipe end correction'),(12,'Rotating bar emf'),(15,'Bohr electron revolutions'),(1,'Flywheel work'),(10,'Galvanometer conversion'),(2,'Liquid-drop pressure'),(10,'Solenoid field'),
(11,'Ferromagnetic domains'),(13,'LCR average power'),(7,'Interference and diffraction'),(14,'Photoelectric equation and photon energy'),(8,'Van de Graaff and displacement current')],98)

pcm('3c9937fdd04c',M,[1,3,6,5,8,9,10,14],[3,4,10,13],[
(1,'Truth-table equivalence'),(2,'Matrix cofactors'),(3,'Principal trigonometric solutions'),(4,'One line of a joint equation'),(6,'Cartesian plane'),(3,'Polar coordinates'),(9,'Tangent equation'),(10,'Trigonometric integral'),(13,'Differential equation'),(9,'Increasing tangent function'),(13,'Family of lines differential equation'),(15,'Binomial parameters'),
(3,'Inverse tangent equation'),(4,'Angle between pairs of lines'),(6,'Parallel-line distance'),(5,'Triangle centroid'),(5,'Section formula proof'),(6,'Vector plane'),(8,'Second derivative identity'),(10,'Trigonometric integral'),(13,'Differential equation'),(9,'Rectangle optimization'),(14,'Expectation of sixes'),(15,'Repeated coin trials'),
(1,'Logical identity'),(2,'Matrix inversion system'),(5,'Concurrent altitudes'),(7,'Graphical optimization'),(8,'Parametric derivative'),(10,'Integration by parts'),(12,'Area between parabolas'),(11,'Definite logarithm integral')],112)
pcm('2c3c5c6b2827',M,[1,3,5,7,8,10,13,14],[4,5,10,13],[
(1,'Inverse and contrapositive'),(2,'Inverse by row operations'),(3,'Polar coordinates'),(4,'Slopes of joint lines'),(5,'Section ratio'),(7,'Graphical inequalities'),(9,'Increasing function'),(10,'Trigonometric integral'),(12,'Area under curve'),(13,'Separable equation'),(14,'Mean random selection'),(12,'Enclosed area'),
(3,'General trigonometric solution'),(3,'Inverse trigonometric identity'),(4,'Angle between pair of lines'),(5,'Perpendicular direction ratios'),(6,'Shortest distance between lines'),(6,'Plane through lines'),(8,'Infinite nested function derivative'),(9,'Approximate sine'),(10,'Integration by parts'),(13,'Particular differential equation solution'),(14,'Continuous distribution'),(15,'Repeated dice trials'),
(1,'Switching circuit simplification'),(2,'Adjoint identity'),(5,'Tetrahedron volume'),(6,'Point-line distance'),(8,'Second derivative identity'),(9,'Lagrange mean value theorem'),(10,'Rational integral'),(11,'Definite integral property')],112)
pcm('852769a971f1',M,[1,3,5,6,8,15,10,12],[1,5,13,9],[
(1,'Logical equivalence'),(2,'Adjoint matrix'),(3,'General tangent solution'),(4,'Joint line equation'),(5,'Direction angles'),(6,'Plane perpendicular to vector'),(9,'Minimum sum of squares'),(10,'Substitution integral'),(11,'Definite integral'),(10,'Trigonometric integral'),(12,'Parabola area'),(14,'Waiting time distribution'),
(1,'Switching table'),(3,'Inverse trigonometric identity'),(3,'Triangle trigonometry'),(5,'Direction ratios and cosines'),(6,'Cartesian/vector line'),(6,'Plane through three points'),(8,'Higher derivatives'),(9,'Particle motion'),(9,'Tangent and normal'),(14,'Coin mean and variance'),(13,'Homogeneous equation'),(15,'Cards with replacement'),
(2,'Matrix inverse'),(4,'Homogeneous pair of lines'),(5,'Coplanar vector decomposition'),(7,'Graphical optimization'),(8,'Parametric derivative'),(10,'Indefinite integral'),(11,'Definite integral property'),(13,'Newton cooling equation')],112)

pcm('bd87340fdded',C,[1,2,4,8,9,11,16,13,5,3],[10,12,15,6,7,9,8,2],[
(6,'Pseudo-first-order reaction'),(1,'Schottky defect'),(10,'Ethyl bromide reactions'),(14,'Peptide linkage'),(2,'Osmotic molar mass'),(9,'Ligand types'),(7,'Group 16 trends'),(11,'Phenol preparation'),(13,'Ethylamine preparation'),(12,'Aldol products'),(4,'Reversible expansion work'),(5,'Reduction charge'),
((8,7),'Haematite and halogen configurations'),(15,'Polymer structural classification'),(16,'Green chemistry and nanotechnology'),((14,12),'Glucose preparation and adipic acid'),(11,'Ether reactions'),(9,'Complex charge classes'),(8,'Spin magnetic moment and ion colour'),((8,12),'Lanthanoid contraction and acetic acid'),(12,'Ketones and iodoform'),(6,'First-order half-life'),(4,'Formation enthalpy'),(3,'Buffer pH'),
((2,1),'Osmosis and crystal density'),((4,3),'First law and pH-pOH'),(5,'Standard hydrogen electrode'),((1,7),'Defect and sulphur chemistry'),(10,'Halogen derivative conversions')],98)
pcm('2656b1092cd2',C,[1,3,6,8,9,10,12,12,14,15],[16,13,10,8,9,2,4,5],[
(8,'Lanthanoids and actinoids'),(2,'Solution mole fraction'),(16,'Green chemistry and nanoparticles'),(1,'Impurity defects'),(10,'Halogen derivative reactions'),(3,'Buffer and solubility product'),(13,'Ethylamine reactions'),(5,'Cell Gibbs energy'),(14,'Glucose and ribose'),(4,'Extensive property and expansion'),(15,'Nylon 6,6'),(7,'Oxoacid structures'),
(2,'Osmosis and boiling elevation'),(11,'Alcohol/phenol/ether conversions'),(3,'Weak acid dissociation'),(10,'Elimination and CFC'),(4,'Reversible expansion'),(8,'Interstitial compounds and alloys'),(5,'Hydrogen-oxygen fuel cell'),(9,'Complex hybridisation'),(6,'Reaction orders and integrated law'),(12,'Aldol condensation'),(7,'Anomalous oxygen'),((12,13),'Acetic acid conversions and amine name'),
((6,8,16),'First-order completion, gadolinium and tyre nanomaterial'),((4,15,14),'Enthalpy relation, vulcanization and peptide bond'),((1,12),'Crystal density and haloform'),((9,5,7),'Stereoisomers, reference electrode and ozone'),((11,7),'Phenol preparation and group 16 properties')],98)
pcm('92fe65dbbe82',C,[8,14,12,3,9,1,15,10,12,6],[16,13,10,9,8,5,4,2],[
(4,'Isothermal expansion work'),(7,'Interhalogens and bleaching powder'),(16,'Nanomaterial and sol-gel'),(14,'Protein classification'),(5,'Copper electrodeposition'),(13,'Amine basicity'),(3,'Acetate buffer'),(10,'Ethyl bromide conversions'),(2,'Henry solubility'),(15,'Polymer monomers'),(8,'Lanthanoid contraction and dichromate'),(1,'Crystal density relation'),
(2,'Osmotic molar mass'),(12,'Named carbonyl reactions'),(4,'Combustion enthalpy'),(10,'Ethyl bromide reactions'),(6,'Rate law'),(7,'Halogen property trends'),(12,'Carbonyl reduction and ketone preparation'),(9,'Werner theory'),(5,'Electrochemical series'),((11,10,13),'Alcohol-halide-nitrile-amine reaction sequence'),(3,'Bronsted theory and pH'),(8,'Dichromate preparation'),
((11,7),'Alcohol/phenol/ether conversions and neon'),((4,14,8),'Thermodynamic definitions, enzymes and transuranics'),((1,16,15),'Crystal lattice, nanoscience and polymerization'),((6,5,7),'Half-life, accumulator and oxoacid'),((9,12),'Nickel complexes and carbonyl conversions')],98)
pcm('8ae579ae23a1',C,[1,2,7,9,4,16,3,12,5,13],[13,12,15,6,2,7,9,8],[
(6,'First-order half-life'),(2,'Henry law and osmotic pressure'),(8,'Lanthanoids and actinoids'),(7,'Anomalous oxygen'),((11,12),'Anisole bromination and carboxylate decarboxylation'),(4,'Pressure-volume work'),(9,'Ionization isomers'),(14,'Glucose preparation'),(5,'Reduction charge'),(11,'Unoxidizable alcohol'),(10,'Halogen conversion sequence'),(12,'Aldehyde preparation'),
((8,7),'Transition configuration and oxoacids'),(3,'Conjugate pair and pH'),(16,'Atom economy and nanomaterials'),((14,10),'Peptide bond and nitroalkane preparation'),(11,'Phenol and ether reactions'),(9,'EAN and cobalt complex'),(8,'Magnetic moment and gadolinium'),((8,13),'Iron reduction and amine reactions'),(12,'Cannizzaro and adipic acid'),(6,'Zero order and intermediate'),(4,'Enthalpy and internal energy'),(15,'Polymer classification and uses'),
((1,2),'Crystal lattice and Raoult law'),((4,3),'Entropy and common ion'),(5,'Lead accumulator'),((1,7),'Unit cell, F-centre and fluorine'),(10,'SN2 and halide reactions')],98)

def english_recent(paper,prose,poem,appreciation):
    for i in range(1,7):add(paper,f'1(A){i}',2,prose,'Seen prose activity')
    for i in range(1,4):add(paper,f'1(B)({i})',1,'Language Study / Grammar','Grammar transformation')
    add(paper,'1(B) error correction',1,'Language Study / Grammar','Error correction')
    for i in range(1,7):add(paper,f'2(A){i}',2,'Unseen Reading Comprehension','Unseen passage activity')
    add(paper,'2(B)',3,'Summary Writing','Summary of unseen passage')
    add(paper,'2(C)',3,'Mind Mapping','Mind-map activity')
    for i in range(1,6):add(paper,f'3(A){i}',2,poem,'Poetry activity')
    add(paper,'3(B)',4,appreciation,'Poetry appreciation')
    genres=[['Virtual Message','Statement of Purpose','Group Discussion'],['E-mail Writing','Report Writing','Interview'],['Speech Writing','Compering','Expansion of Idea'],['Review Writing','Blog Writing','Appeal']]
    for group,names in zip('ABCD',genres):
        for i,name in enumerate(names,1):add(paper,f'4({group}) alternative {i}',4,name,'Writing task; choose one of three in this group')
    for part,name in zip('ABCD',['History of the Novel','To Sir, with Love','Around the World in Eighty Days','The Sign of Four']):
        for i in range(1,3):add(paper,f'5({part})({i})',2,name,'Novel activity')
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==112
    REVIEWS[paper]={'offeredMarks':112,'maxMarks':80,'reviewNote':'All three alternatives in each writing task are counted: 48 offered writing marks, of which 16 are attempted. English includes named literature and language skills.'}
english_recent('e154776f1b04','The Cop and the Anthem','Song of the Open Road','Have You Earned Your Tomorrow')
english_recent('1f2febed4131','Voyaging Towards Excellence','The Inchcape Rock','She Walks in Beauty')
english_recent('ca63d8c3caba','Why We Travel','She Walks in Beauty','The Inchcape Rock')
english_recent('2c2b8d014803','Voyaging Towards Excellence','Song of the Open Road','Have You Earned Your Tomorrow')
english_recent('c7a91da55678','The Cop and the Anthem','Father Returning Home','Indian Weavers')
for item in Q:
    if item['paperId']=='1f2febed4131' and item['question'] in ['3(A)3','3(A)4','3(A)5']:
        item['chapter']='Printing-error credit (2023)'
        item['topic']='Erroneous poetry activity; six marks of conditional board credit, not a normal question'
        item['erratumSource']='https://indianexpress.com/article/cities/mumbai/students-who-attempted-erroneous-questions-in-english-paper-will-get-6-marks-says-state-board-8479675/'
REVIEWS['1f2febed4131']['reviewNote']+=' Poetry activities A3-A5 had printing errors; their six marks are a separate administrative bucket.'

P.update({17:'Gravitation (legacy)',18:'Elasticity (legacy)',19:'Communication Systems (legacy)',20:'Doppler Effect in Sound (legacy)'})
C.update({17:'p-Block: Group 15 (legacy)',18:'Nitro Compounds (legacy)',19:'Chemistry in Everyday Life (legacy)',20:'Metallurgy (legacy)',21:'Biomolecules: Lipids (legacy)'})
def legacy(paper,d,groups):
    from parse_legacy import parse
    ps=json.loads((ROOT/'data/papers.json').read_text());p=next(p for p in ps if p['id']==paper)
    items=parse(p);keys=[k for group in groups for k in group]
    assert len(items)==len(keys),(paper,len(items),len(keys))
    assert sum(x['marks'] for x in items)==98,(paper,'incorrect offered total')
    for item,k in zip(items,keys):add(paper,item['question'],item['marks'],label(d,k),'Legacy paper; topic mapped to current chapter where content corresponds')
    REVIEWS[paper]={'offeredMarks':98,'maxMarks':70,'reviewNote':'All offered questions reviewed. Historical content uses a chapter crosswalk; legacy topics remain separate. Unspecified mixed-question splits stay joint.'}
legacy('971e07a83123',C,[[1,6,7,2,4,5,20],[1,5,5,17,4,20,2,6],[2,6,4,17],[(4,20,1),(7,5,2)],[8,10,12,9,14,13,12],[8,11,15,10,18,19,12,(14,21)],[8,12,(21,14),9],[(15,19,11,10),(13,11,12)]])
legacy('05bf0da8ea6d',C,[[(2,4,5),(6,20,7)],[4,2,7,1],[17,5,20,6,4,17,2,1],[1,5,7,20,6,4,2],[(11,14),(19,15,12)],[13,12,8,9],[19,18,12,15,21,10,8,11],[9,10,14,13,15,12,8]])
legacy('fef3b9a9ebdd',C,[[1,4,2,5,20,17,6],[4,2,1,6,5,7,20,5],[4,2,6,17],[(1,4,20),(7,5)],[10,9,8,18,11,12,14],[12,13,19,12,14,8,12,15],[9,8,12,14],[(13,15,19),(11,10)]])
legacy('1dd5aac29de5',C,[[1,2,4,6,20,17,4,20],[1,2,4,5],[(17,7,5,2),(20,5,6)],[7,7,4,2,20,5,6],[8,9,10,11,12,18,19,(14,15)],[8,(10,9,8),(9,10),(19,15)],[(12,11),(14,18)],[10,11,12,13,14,15,19]])
legacy('dbcaa8f358ec',C,[[17,4,17,20,1,5,6],[5,6,20,2,4,17,1,7],[17,5,4,6],[(5,7,1,2),(20,1,4,2)],[13,10,9,8,11,14,11],[11,13,12,19,14,8,15,(10,12)],[9,8,12,(14,21)],[(13,15,19),(10,11)]])
legacy('6d2f0ed58142',P,[[1,2,18,6,3,5,3],[17,1,3,5,5,2,2,1],[1,17,1,18],[(5,20),(6,3)],[7,9,14,15,16,19,13],[8,7,10,10,11,8,19,15],[16,9,15,14],[(12,10),7]])
legacy('855e96ba1b7e',P,[[2,3,17,6,3,1,1,1],[17,18,5,6],[(1,2),(6,5)],[1,18,3,6,5,6,3],[11,14,7,11,14,19,12,14],[10,15,16,8],[7,(12,9)],[8,16,19,9,15,9,7]])
legacy('5ad889a918fb',P,[[1,1,5,18,6,17,3],[1,17,1,(3,4),5,2,1,17],[2,20,3,18],[(5,6),(5,1)],[8,9,14,15,16,19,7],[7,10,11,19,10,10,12,15],[15,16,8,14],[(12,9),7]])
legacy('8d5730d136ee',P,[[4,18,1,5,6,6,3],[1,3,5,2,17,1,6,3],[17,1,2,1],[(5,6),(6,18)],[13,14,11,19,16,14,8],[7,10,9,19,10,12,9,15],[16,12,8,15],[7,(15,14)]])

def manual_legacy(paper,d,groups,marks):
    for n,(keys,mark) in enumerate(zip(groups,marks),1):
        for i,k in enumerate(keys,1):add(paper,f'{n}.{i}',mark,label(d,k),'Legacy paper; reviewed chapter crosswalk')
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==98
    REVIEWS[paper]={'offeredMarks':98,'maxMarks':70,'reviewNote':'All offered question groups checked against the paper. Legacy topics and unspecified mixed marks are kept separate.'}
manual_legacy('a92405463d24',P,[[1,17,1,3,1,6,5,2],[1,18,18,6,6,3,1],[(5,3),6],[17,1,2,18],[7,10,11,19,10,11,12,15],[7,7,8,9,14,16,19],[(12,8),(15,14)],[7,7,9,16]],[2,1,7,3,2,1,7,3])
manual_legacy('b26ff4aee429',P,[[6,20,1,18,5,3,1],[17,3,1,1,6,2,1,5],[2,1,18,17],[(5,3),6],[19,7,8,9,14,16,7],[7,10,19,11,15,13,14,10],[9,16,7,7],[(12,8),(15,14)]],[1,2,3,7,1,2,3,7])
manual_legacy('8e72a3a7437a',C,[[4,1,5,20,17,2,6],[2,4,5,1,6,(2,5),(7,17),20],[(17,7),1,5,4],[(4,7,2),(20,7,6)],[15,14,9,11,8,10,19],[8,9,11,12,13,14,19,10],[(10,12),11,15,(14,9)],[(8,19,14,13),(12,13)]],[1,2,3,7,1,2,3,7])

cs('2a533f39423c',CS1,[1,2,3,4,2,2,1,1,3,1,1,2,3,1,1,3,2,4,3,4,3,4,3,3,4,3,3,4])
cs('b873aa00ad01',CS1,[4,1,3,2,1,2,4,2,3,2,1,3,4,1,3,2,1,3,1,3,3,1,3,3,4,3,3,4])

cs('bb031cc273ad',CS2,[1,2,4,5,1,1,4,2,5,2,1,5,5,1,5,5,2,1,4,3,2,3]+[2]*6)
cs('5cdf065763ca',CS2,[1,2,4,5,1,1,3,4,5,1,1,5,2,2,2,5,1,2,1,5,4,5]+[2]*6)
cs('ba4915db5bbd',CS2,[1,2,1,4,1,2,3,4,5,2,1,5,1,2,1,5,1,2,1,5,4,5]+[2]*6)

cs('d52cab8c0258',CS1,[1,2,3,4,3,3,1,3,2,1,3,1,2,3,2,2,1,4,3,1,1,3,3,3,4,3,3,4])
cs('9beafdad83b6',CS1,[1,2,3,4,1,1,2,3,4,3,3,1,1,3,2,3,1,3,2,2,2,1,3,3,4,3,3,4])
cs('9e56d1be740c',CS2,[1,2,3,5,1,2,5,1,5,2,4,1,1,2,5,4,5,3,2,1,1,5]+[2]*6)

cs('4520b6d86eab',CS1,[1,2,3,4,1,2,3,3,2,1,2,1,2,3,4,1,3,1,3,2,3,1,3,3,4,3,3,4])

M.update({16:'Continuity (legacy)',17:'Limits (legacy)'})
pcm('7cab204ab871',P,[9,12,1,6,7,7,2,15,18,6],[19,4,12,1,5,15,17,8],[
(14,'Photoelectric definitions'),(12,'Transformer comparison'),(19,'Sky wave propagation'),(1,'Circular acceleration'),(3,'Kinetic gas law'),(15,'Bohr postulates'),(7,'Resolving power'),(14,'Photoelectric threshold'),(13,'LC resonance'),(6,'Stretched string'),(1,'Wheel inertia'),(15,'Bohr energy'),
(17,'Gravitation'),(5,'SHM equation'),(20,'Sound Doppler'),(1,'Parallel axis theorem'),(8,'Parallel-plate capacitor'),(18,'Elastic constants'),(3,'Radiation spectrum'),(7,'Biprism wavelength'),(5,'Pendulum energy'),(7,'Refractive indices'),(1,'Circular cage motion'),(9,'Meter bridge'),
(6,'Open pipe harmonics'),(16,'Full-wave rectifier'),(2,'Capillarity and bubble work'),(10,'Moving coil galvanometer'),((11,10),'Orbital and coil magnetic moments')],98)
pcm('b69637d9ccb4',C,[15,7,8,9,10,13,14,19,1,4],[2,11,12,13,20,4,5,6],[
(4,'Hess law'),(5,'Cell potential'),(6,'Order and molecularity'),(7,'Noble gas uses'),((20,13),'Zinc ore and ammonium salt'),(8,'Dichromate reactions'),(14,'Glucose optical activity'),(11,'Etherification'),(12,'Acyl reaction sequence'),(14,'Glucose and hormones'),(1,'Solid types'),(2,'Solution definitions'),
(20,'Flux and leaching'),((7,17),'Sulphurous acid and nitrogen'),(8,'Transition configurations and colour'),(9,'EAN and ionization isomerism'),(10,'Chlorobenzene reactions'),(11,'Alcohol preparation'),(18,'Nitroalkane tests'),(14,'Monosaccharides and denaturation'),(15,'Terylene'),(19,'Soaps and antiseptic'),(1,'Crystal lattice'),(6,'Reaction rate'),
(5,'Series and corrosion'),(7,'Interhalogens and oxygen'),(12,'Aldol and acid uses'),(2,'Boiling-point molar mass'),(4,'Thermodynamic definitions and bond enthalpy')],98)
pcm('015624b70dc7',M,[3,5,6,6,16,9,11,13],[1,3,8,15],[
(1,'De Morgan truth table'),(2,'Cofactors'),(4,'Angle of joint lines'),(5,'Collinear vectors'),(5,'Direction cosines'),(1,'Switching circuit'),(8,'Logarithmic derivative'),(10,'Rational integral'),(10,'Trigonometric integral'),(13,'Differential equation'),(14,'Expectation'),(8,'Second derivative'),
(1,'Converse inverse contrapositive'),(3,'Inverse sine identity'),(5,'Coplanar points'),(5,'Right triangle vectors'),(6,'Perpendicular line'),(6,'Point-plane distance'),(8,'Implicit derivative'),(9,'Related rates'),(9,'Approximate exponential'),(10,'Substitution integral'),(13,'Linear equation'),(14,'Probability density'),
(4,'Homogeneous pair of lines'),(7,'Graphical optimization'),(2,'Matrix reduction'),(3,'Half-angle triangle identity'),(16,'Piecewise continuity'),(10,'Integral identity'),(15,'Repeated coin trials'),(11,'Definite integral symmetry')],112)

def pcm2019(paper,d,first,short,medium,extras,longparts):
    for n,k in enumerate(first,1):add(paper,str(n),1,label(d,k),'MCQ / very short answer')
    for n,k in enumerate(short,9):add(paper,str(n),2,label(d,k),'Short answer')
    for n,k in enumerate(medium,16):add(paper,str(n),3,label(d,k),'Medium answer')
    for n,mark,k in extras:add(paper,f'{n} OR',mark,label(d,k),'Internal alternative')
    for n,mark,k in longparts:add(paper,n,mark,label(d,k),'Long-answer subpart; separately printed marks')
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==90
    REVIEWS[paper]={'offeredMarks':90,'maxMarks':70,'reviewNote':'2019 paper pattern: compulsory items plus five internal alternatives. Printed long-answer subpart marks retained separately.'}
pcm2019('b45ca696cdd2',P,[2,3,8,14,1,11,12,16],[7,11,5,8,1,16,19],[1,17,18,2,6,14,3,9,10,13,15],[(11,2,5),(26,3,15)],[(f'{n}{branch}({i})',mark,k) for n,keys in [(27,[6,1]),(28,[5,6]),(29,[7,7])] for branch in ['A','B'] for i,(mark,k) in enumerate(zip([3,2],keys),1)])
pcm2019('7ac6ea6bd23c',C,[12,8,20,4,19,14,17,1],[11,19,20,5,2,4,11],[15,14,13,10,9,(7,17),6,5,4,2,1],[(12,2,5),(24,3,4)],[(f'{n}{branch}({i})',mark,k) for n,keys in [(27,[13,12]),(28,[10,8]),(29,[6,7])] for branch in ['A','B'] for i,(mark,k) in enumerate(zip([1,4],keys),1)])

def maths2019():
    paper='ce213897be2b'
    keys=[3,6,5,16,10,13,1,5,5,6,8,9,10,10,3,5,6,16,14,15,1,2,3,4,7,8,9,10,11,13]
    for n,k in enumerate(keys,1):add(paper,str(n),1 if n<=6 else 2 if n<=14 else 3 if n<=20 else 4,label(M,k),'2019 question')
    for n,k in [(8,5),(15,3),(19,14),(23,3),(27,9),(30,13)]:add(paper,f'{n} OR',2 if n<=14 else 3 if n<=20 else 4,label(M,k),'Internal alternative')
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==100
    REVIEWS[paper]={'offeredMarks':100,'maxMarks':80,'reviewNote':'2019 pattern: 30 compulsory questions and six internal alternatives; 100 printed marks.'}
maths2019()

P.update({21:'Optical Fibres / Ray Optics (legacy)',22:'Thermoelectricity (legacy)'})
def half_science(paper,d,groups,style='physics'):
    config=[('1',1),('2(A)',2),('2(B)',3),('3(A)',2),('3(B)',3),('4(A)',2),('4(B)',4)]
    config += [('5',4)] if style=='physics' else [('5(A)',4),('5(B)',2)]
    assert len(groups)==len(config)
    for (group,mark),keys in zip(config,groups):
        for i,k in enumerate(keys,1):add(paper,f'{group}({i})',mark,label(d,k),'Historical Paper I/II; archive-attributed year')
    total=sum(q['marks'] for q in Q if q['paperId']==paper)
    assert total==(60 if style=='physics' else 62),(paper,total)
    REVIEWS[paper]={'offeredMarks':total,'maxMarks':40,'reviewNote':'Pre-2013 separate subject part. Year/session follow source archive attribution; the retyped paper does not print a date. Offered alternatives counted.'}
half_science('ec5db2e79dc6',P,[[6,1,5,6,17,18,3,1],[6,2],[1,1,3],[1,1],[3,18,3],[18,4,5],[6,2],[17,6,5]])
half_science('a3ff577f4536',P,[[7,8,14,21,22,16,7,10],[9,7],[10,12,19],[7,10],[8,9,14],[7,8,15],[7,16],[11,15,13]])

half_science('8c8dfcc70bb2',P,[[3,5,6,1,17,1,5,18],[3,1],[6,18,1],[5,3],[1,3,6],[2,1,18],[5,3],[17,2,6]])
half_science('515f1eeead97',P,[[7,10,11,7,16,19,15,8],[7,8],[12,10,11],[9,10],[8,15,19],[7,7,14],[16,14],[7,9,13]])
half_science('c789ad2a68d1',P,[[17,1,18,2,6,3,5,3],[1,18],[2,6,3],[2,5],[1,18,3],[1,4,3],[17,11],[6,6,1]])
half_science('5bb8d9556210',P,[[9,10,13,1,16,19,7,8],[9,15],[8,7,10],[16,10],[19,9,14],[12,8,16],[7,11],[7,13,14]])
half_science('fa6f67f69c18',P,[[6,6,18,5,1,17,1,3],[18,3],[1,5,1],[2,3],[4,5,18],[1,1,6],[17,2],[3,6,6]])


P.update({23:'Lasers and Masers (legacy)'})
C.update({22:'Nuclear Chemistry (legacy)',23:'Gaseous State (legacy)'})
half_science('7f636e28cdbd',P,[[7,7,11,12,16,21,14,10],[15,8],[9,11,19],[7,16],[22,23,14],[12,16,10],[7,8],[13,7,10]])
def half_chem(paper,groups):
    config=[('1',1),('2(A)',2),('2(B)',2),('2(C)',2),('3(A)',3),('3(B)',3),('3(C)',2),('4(A)',4),('4(B)',4),('5(A)',4),('5(B)',2)]
    for (group,mark),keys in zip(config,groups):
        for i,k in enumerate(keys,1):add(paper,f'{group}({i})',mark,label(C,k),'Historical Chemistry part; alternatives included')
    total=sum(q['marks'] for q in Q if q['paperId']==paper)
    assert total==60,(paper,total)
    REVIEWS[paper]={'offeredMarks':60,'maxMarks':40,'reviewNote':'Separate pre-2013 part. Archive-attributed year/session; no printed date in retyped copy. Joint marks are not split without a printed allocation.'}
half_chem('74505e7a0c22',[[8,2,6,4,22,3,5,4],[2,23],[3,5],[6,20],[3,22],[6,8],[(2,5)],[4],[5,2],[4,3],[2,5,22]])
half_chem('8403066a5ebd',[[8,11,11,13,15,19,12,10],[8,11],[13,15],[10,10],[12,14],[21,(11,12)],[13],[11],[10,12],[10,12],[11,19,8]])
half_chem('2ccb4ba4b18b',[[4,3,5,22,6,20,2,4],[5,2],[4,(6,8)],[5,6],[2,3],[5,22],[6],[3],[4,(20,6)],[2,4],[3,5,22]])
half_chem('8b7d745ffe61',[[8,10,11,12,11,13,14,11],[12,13],[10,15],[11,12],[10,(11,12)],[11,14],[11],[10],[8,(15,19)],[10,12],[11,13,21]])
half_chem('05ed7aa084c3',[[4,3,5,22,6,8,4,2],[2,22],[6,8],[(2,22),3],[6,3],[20,5],[4],[5],[2,4],[4,3],[22,5,2]])
half_chem('57d5a1ea06cc',[[11,19,10,11,12,14,8,13],[(15,10),(12,14)],[8,10],[12,21],[10,11],[10,(11,12)],[8],[11],[13,12],[12,10],[15,14,19]])
half_chem('a942553937e5',[[8,2,6,4,22,3,5,4],[2,4],[3,5],[6,20],[3,22],[6,8],[(2,5)],[4],[5,2],[4,3],[2,5,22]])
half_chem('9702e6cfd2f8',[[8,10,11,12,12,13,14,15],[10,19],[12,14],[15,13],[12,11],[11,10],[8],[10],[12,11],[10,(13,21)],[8,12,(19,14)]])
cs('4133cb63fd11',CS2,[2,1,5,4,2,5,2,5,1,5,2,5,4,2,3,2,3,1,4,1,1,5]+[2]*6)
cs('fe754e74bb6b',CS1,[1,2,3,4,1,2,4,3,2,1,1,3,1,2,3,1,2,1,3,3,2,3,3,3,4,3,3,4])
cs('b038cd08a266',CS2,[1,2,4,5,1,2,5,1,2,5,1,3,1,1,4,4,5,1,2,5,1,5]+[2]*6)
cs('81c78cf73059',CS1,[1,2,3,4,1,2,4,1,2,3,1,3,1,2,3,2,3,1,2,3,1,2,3,3,4,3,3,4])
cs('66017371b88d',CS2,[2,3,1,5,1,4,5,1,5,2,1,2,4,3,5,2,1,1,4,5,1,5]+[2]*6)


cs('b79134a43bfc',CS1,[3,2,1,3,2,3,1,4,3,2,3,1,2,3,1,2,3,1,2,3,1,3,3,3,4,4,4,3])
cs('e1783c14ad07',CS2,[2,1,4,5,1,2,5,1,2,5,1,3,1,1,4,4,5,1,2,5,1,5]+[2]*6)
M.update({18:'Circles (legacy)',19:'Conic Sections (legacy)',20:'Correlation and Regression (legacy)',21:'Finite Differences (legacy)',22:'Boolean Algebra (legacy)',23:'Probability of Events (legacy)',24:'Solids of Revolution (legacy)'})
def legacy_math(paper,groups):
    config=[('1(A)',2),('1(B)',2),('2(A)',3),('2(B)',4),('3(A)',3),('3(B)',4),('4(A)',2),('4(B)',2),('5(A)',3),('5(B)',4),('6(A)',3),('6(B)',4)]
    assert len(groups)==12
    for (group,mark),keys in zip(config,groups):
        for i,k in enumerate(keys,1):add(paper,f'{group}({i})',mark,label(M,k),'Historical mathematics chapter crosswalk')
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==116
    REVIEWS[paper]={'offeredMarks':116,'maxMarks':80,'reviewNote':'2013-2018 pattern: all printed alternatives counted (116 offered marks). Historical-only chapters are retained separately.'}
legacy_math('d022e7311887',[[5,2,3],[5,3,6,6,1],[1,6,3],[2,4,5],[1,4,3],[5,6,7],[8,9,14],[8,9,10,13,15],[13,10,16],[8,9,10],[16,13,15],[10,12,14]])
legacy_math('ab24bcad55f8',[[2,3,5],[1,5,6,6,5],[5,1,5],[4,3,2],[4,6,1],[3,6,7],[14,11,13],[10,8,12,13,15],[10,8,16],[9,13,11],[16,8,15],[9,13,14]])
legacy_math('2690306e711c',[[1,3,4],[2,6,5,4,6],[1,5,6],[3,7,2],[5,1,4],[6,6,3],[16,9,15],[8,9,12,14,10],[8,15,11],[16,10,13],[11,10,8],[13,9,14]])
legacy_math('c09bab398848',[[2,3,4],[1,4,6,6,5],[5,1,5],[5,3,2],[4,6,1],[3,6,7],[14,11,13],[10,8,10,8,15],[10,8,16],[9,10,11],[16,8,14],[9,13,14]])
legacy_math('8eec1fb4e111',[[5,2,3],[5,6,6,5,1],[6,5,1],[3,4,2],[4,1,5],[6,7,3],[8,13,9],[16,9,10,14,15],[8,13,10],[9,11,16],[13,15,8],[12,10,14]])
legacy_math('88096937e5c4',[[3,5,19],[1,2,4,18,3],[1,4,19],[2,3,5],[1,18,6],[19,7,6],[9,10,13],[8,9,12,20,24],[16,8,10],[15,9,13],[10,14,15],[8,12,20]])
def half_math(paper,groups):
    config=[('1(A)',3),('1(B)',2),('2(A)',3),('2(B)',2),('3(A)(a)',3),('3(A)(b)',3),('3(B)',2),('4(A)(a)',3),('4(A)(b)',3),('4(B)',2),('5(A)(a)',3),('5(A)(b)',3),('5(B)',2)]
    for (group,mark),keys in zip(config,groups):
        for i,k in enumerate(keys,1):add(paper,f'{group}({i})',mark,label(M,k),'Pre-2013 mathematics part; archive-attributed year')
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==74
    REVIEWS[paper]={'offeredMarks':74,'maxMarks':40,'reviewNote':'Separate historical part with 74 marks across all alternatives. Year/session attributed by archive; no printed date in retyped copy.'}
half_math('31962e3f7bcc',[[1,1,1],[4,18],[5,5,5],[19,19],[2,2],[4,18],[5,5],[4,18],[23,23],[19,19],[19,19],[6,6],[7,7]])
half_math('e0f1f0113cf7',[[1,1,1],[4,18],[5,5,5],[5,5],[2,2],[4,18],[7,7],[4,18],[23,14],[19,19],[19,19],[6,6],[19,19]])
half_math('f79341fafca8',[[17,16,16],[10,10],[8,8,9],[13,13],[10,10],[10,10],[8,8],[21,21],[13,13],[22,22],[8,8],[10,11],[22,22]])


half_math('79701a433922',[[1,1,1],[7,7],[5,5,5],[5,5],[2,2],[4,18],[4,18],[4,18],[23,23],[19,19],[19,19],[6,6],[19,19]])
half_math('9ca1c5ce5df8',[[17,17,16],[10,10],[8,8,9],[8,8],[10,10],[11,11],[13,13],[21,21],[13,13],[22,22],[8,8],[10,11],[22,22]])
def half_math2009(paper,groups,second=False):
    if not second:config=[('1(A)',3),('1(B)',2),('2(A)(a)',3),('2(A)(b)',3),('2(B)',2),('3(A)(a)',3),('3(A)(b)',3),('3(B)',2),('4(A)',3),('4(B)',2),('5(A)(a)',3),('5(A)(b)',3),('5(B)',2)]
    else:config=[('1(A)',3),('1(B)',2),('2(A)(a)',3),('2(A)(b)',3),('2(B)',2),('3(A)',3),('3(B)',2),('4(A)(a)',3),('4(A)(b)',3),('4(B)',2),('5(A)(a)',3),('5(A)(b)',3),('5(B)',2)]
    for (group,mark),keys in zip(config,groups):
        for i,k in enumerate(keys,1):add(paper,f'{group}({i})',mark,label(M,k),'Historical mathematics part')
    assert sum(q['marks'] for q in Q if q['paperId']==paper)==74
    REVIEWS[paper]={'offeredMarks':74,'maxMarks':40,'reviewNote':'All printed alternatives mapped; archive-attributed year/session for retyped historical part.'}
half_math2009('bac68f061f07',[[5,5,5],[4,18],[19,19],[6,6],[5,5],[4,18],[23,14],[19,19],[1,1,1],[7,7],[2,2],[4,18],[19,19]])
half_math2009('7eba3d33f8bd',[[17,17,16],[13,13],[21,21],[13,13],[22,22],[8,8,9],[22,22],[8,8],[10,11],[10,10],[10,10],[11,11],[8,8]],True)


# Older English is reviewed at section resolution. Do not invent old text titles,
# or mix its required section marks with modern offered alternative marks.
for paper in ['946f6269c654','c0604be0f6c3','312e79c34ad8','420e6322c5f3','9746a5f80347','34a0a42ff0c5','ec462542da80','7da6ea074b56','e6e170c4e1b9','2005a50d8d37','77bcf591ee3b','8debfcbbb76f','c7868edf3d1a']:
    for ref,chapter,marks in [('1-3','Reading, Language Study, Notes & Summary',45),('4','Poetry',8),('5','Rapid Reading & Composition (legacy)',8),('6-7','Written Communication',19)]:
        add(paper,ref,marks,chapter,'Required section allocation; not individual literature chapter attribution')
        Q[-1].update(marksBasis='required-section',resolution='section')
    REVIEWS[paper]={'requiredMarks':80,'maxMarks':80,'analysisResolution':'section','reviewNote':'Section totals reviewed (80 required marks). Older literature chapter titles and individual alternative distributions are not mapped; excluded from offered chapter rankings.'}

cs('5500d129312c',CS1,[4,3,1,1,1,3,2,1,3,2,3,3,3,4,1,3,1,3,3,2,1,1,3,3,4,3,3,4])
cs('1b2c52e0d149',CS2,[4,2,5,2,4,1,5,1,3,4,1,3,2,5,5,1,3,5,5,3,4,5]+[2]*6)

cs('9f5ef2bf01ca',CS2,[1,2,4,5,1,2,4,1,2,5,1,5,1,1,5,2,3,2,2,5,3,5]+[2]*6)
cs('a17cf534ba01',CS1,[2,4,1,2,1,2,3,1,3,2,1,3,1,4,3,3,2,2,3,1,3,2,3,3,4,3,3,4])
cs('bd4b166378c1',CS1,[2,4,3,3,1,3,4,3,1,2,1,3,1,3,3,1,2,2,1,3,1,3,3,3,4,3,3,4])
cs('1fe78b373a54',CS1,[4,2,1,3,1,4,2,3,2,2,1,3,1,3,3,1,2,3,2,3,3,1,3,3,4,3,3,4])
cs('256b5adb0229',CS1,[1,2,3,4,1,2,4,3,2,2,1,3,3,1,3,1,2,2,1,3,3,1,3,3,4,3,3,4])
cs('ab62462405d1',CS2,[1,4,2,5,1,2,5,1,2,5,3,2,1,2,5,1,4,2,2,4,5,5]+[2]*6)
cs('36fc2a580213',CS2,[5,4,2,1,1,4,2,1,5,2,1,3,5,1,4,4,1,5,2,2,5,5]+[2]*6)

def publish():
    papers=json.loads((ROOT/'data/papers.json').read_text())
    for p in papers:
        if p['id'] in REVIEWS:
            p.update(REVIEWS[p['id']]);p['analysisStatus']='complete';p['status']='verified'
    sections=[]
    for p in papers:
        if p['subject']!='English' or p['id'] not in REVIEWS:continue
        if p.get('analysisResolution')=='section':
            sections.extend(q for q in Q if q['paperId']==p['id'])
        else:
            for ref,name,mark in [('1-2','Reading, Language Study, Notes & Summary',34),('3','Poetry',8 if p['year']==2023 else 14),('4','Written Communication',16),('5','Novel',16)]:
                sections.append({'paperId':p['id'],'question':ref,'chapter':name,'marks':mark,'marksBasis':'required-section','resolution':'section','reviewed':True})
            if p['year']==2023:sections.append({'paperId':p['id'],'question':'3A3-5','chapter':'Printing-error credit (2023)','marks':6,'marksBasis':'required-section','resolution':'section','reviewed':True})
    (ROOT/'data/english-sections.json').write_text(json.dumps(sections,indent=2))
    (ROOT/'data/questions.json').write_text(json.dumps(Q,indent=2))
    (ROOT/'data/papers.json').write_text(json.dumps(papers,indent=2))
    (ROOT/'data/status.json').write_text(json.dumps({'message':f'{len(REVIEWS)} unique PDFs reviewed. All 15 failed paper entries recovered from alternate sources, including public scans. The 2007–2026 collection still has historical gaps. Thirteen older English papers have section-level analysis only.'}))
    print(len(REVIEWS),'papers',len(Q),'question items')
if __name__=='__main__':publish()
