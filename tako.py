from widget import Widget
import scipy
import math
import caffe
import random
from pygame import sprite, Color, Rect
import os
from textwrap import dedent
import genetics

# a Tako is a creature and also a Widget
# it has a neural net (agent)
# it had a genetics-like system before pycaffe
# it has drives (boredom, hunger, etc)
# it is meant to live in a Garden
class Tako(Widget):
    node = 4
    dir_map = {0: "north.png", 1: "east.png", 2: "south.png", 3: "west.png"}

    #gen is short for generation, not genome or the like
    def __init__(self, dire, x, y, genome, ident, parents, gen=0):
        sprite.Sprite.__init__(self)
        self.direction = dire
        self.x = x
        self.y = y
        self.genome = genome
        self.ident = ident
        #note to self: these three lines need to be disabled to run test suite
        self.image, self.rect = self.load_image(self.dir_map[dire],
                                                Color('#FF00FF'))
        self.rect = Rect(x*50, y*50, 50, 50)
        self.hunger = 150
        self.boredom = 150
        self.pain = 0
        self.desire = 0.0
        self.last_hunger = 150
        self.last_boredom = 150
        self.last_pain = 0
        self.last_desire = 0
        self.last_obj = None
        self.last_action = -1
        self.age = 0
        self.dez = 0
        self.children = []
        self.parents = parents
        self.gen = gen
        #net = caffe.Net('alife.text', '1461257654.3.txt', caffe.TRAIN)
        self.solver = self.make_solver()
        #self.solver = caffe.AdaDeltaSolver('solver.text')
        #uncomment to read in weights from saved network (specify under 'net' above)
        #for pr in net.params.keys():
        #    self.solver.net.params[pr][0].data[...] = net.params[pr][0].data[...]
        #do not delete; keeps synchedmem error from occuring
        #for some reason
        for key in self.solver.net.params:
            print key
            print self.solver.net.params[key][0].data
                    
    @staticmethod
    def default_tako(direction, x, y):
        data = genetics.layer_gene(5, False, False, 0, "data",
                                        [], 9, "input")
        reward = genetics.layer_gene(5, False, False, 0, "reward",
                                         [], 6, "input")
        stm_input = genetics.layer_gene(5, False, False, 0, "stm_input",
                                             ["data", "reward"], 6, "input")
        stm = genetics.layer_gene(5, False, False, 0, "STM",
                                       ["stm_input"], 6, "STMlayer")
        concat = genetics.layer_gene(5, False, False, 0, "concat_0",
                                          ["data", "STM"], None, "concat")
        action = genetics.layer_gene(5, False, False, 0, "action",
                                          ["concat_0"], 6, "IP")
        loss = genetics.layer_gene(5, False, False, 0, "loss",
                                        ["action", "reward"], 6, "loss")
        layers = [data, reward, stm_input, stm, concat, action, loss]
        weights = []
        with open("default weights.txt") as f:
            for n in range(6):
                for m in range(15):
                    t = f.readline()
                    t = float(t[0:-1])
                    iden = str(n) + " " + str(m)
                    if m < 9:
                        in_layer = "data"
                        m_adj = m
                    else:
                        in_layer = "STM"
                        m_adj = m - 9
                    w = genetics.weight_gene(5, True, False, 3, iden,
                                             t, m_adj, n, in_layer, "action")
                    weights.append(w)
        default_genome = genetics.genome(layers, layers, weights, weights)
        return genetics.genome.build(default_genome, direction, x, y)
            
            
    #drives go DOWN over time
    #except for desire, which has a sine wave funtion
    def update(self):
        self.age += 1
        self.last_hunger = self.hunger
        self.last_boredom = self.boredom
        self.last_pain = self.pain
        self.last_desire = self.desire
        self.hunger -= 0.5
        self.boredom -= 0.5
        if self.pain > 0:
            self.pain = self.pain*.6
            if self.pain < 1:
                self.pain = 0
        self.dez += 1
        if self.dez == 503.0:
            self.dez = 0.0
        #this makes a wave between 0 and 150 with a period of 502 ticks
        self.desire = (math.sin((self.dez/80.0)+11.0)*75.0)+75.0
        self.update_sprite()

    def update_sprite(self):
        #if we moved, moved the sprite
        #if self.last_action == 0:
        #    self.rect = Rect.((self.x * 50), (self.y * 50), 50, 50)
        #if we turned, update the sprite
        if self.last_action == 1 or self.last_action == 2:
            self.image, temp = self.load_image(self.dir_map[self.direction], -1)
        
    def update_drives(self, drive, modifier):
        if drive == "hunger":
            self.hunger += modifier
            if self.hunger > 150:
                self.hunger = 150
        elif drive == "boredom":
            self.boredom += modifier
            if self.boredom > 150:
                self.boredom = 150
        elif drive == "pain":
            self.pain += modifier
        elif drive == "desire":
            self.desire += modifier

    def modify(self, result):
        #print(result)
        if result is not None:
            for x in range(len(result)):
                if x%2 == 0:
                    drive = result[x]
                else:
                    modifier = result[x]
                    self.update_drives(drive, modifier)
                    
    def make_solver(self):
        ident_file = os.path.join('Gen files', self.ident)
        ident_file = ident_file + '.gen'
        result = dedent('''\
                        net: "{0}"
                        solver_type: ADADELTA
                        momentum: 0.95
                        base_lr: 0.2
                        lr_policy: "step"
                        gamma: 0.1
                        stepsize: 1000000
                        max_iter: 2000000
                        display: 10000
                        '''.format(ident_file))
        f = open("temp_solver.txt", "w")
        f.write(result)
        f.close()
        solver = caffe.AdaDeltaSolver('temp_solver.txt')
        os.remove('temp_solver.txt')
        return solver

    def played(self):
        return ("boredom", 15)

    def mated(self, tak):
        if tak.desire >= 100:
            if self.desire >= 100:
                self.dez = 0
                self.desire = 0
                tak.dez = 0
                tak.desire = 0
                return [("boredom", 45), ("hunger", -10), ("desire", -150),
                self.genome.recombine(tak.genome), [self.ident, tak.ident],
                        (max(self.gen, tak.gen) + 1)]
            else:
                return ("boredom", -1)
        else:
            return ("boredom", -1)
        

class STMlayer(caffe.Layer):

    def setup(self, bottom, top):
        self.blobs.add_blob(6)

    def forward(self, bottom, top):
        #action # is fed directly in
        act = bottom[0].data.flatten()
        action = act[0]
        ftop = top[0].data.flatten()
        if action >= 0:
            for x in range(len(ftop)):
                if x == action:
                    #means that this was the selected action
                    top[0].data[0][0][0][x] += 1
                else:
                    #if not selected action, decay the memory
                    if top[0].data[0][0][0][x] != 0:
                        top[0].data[0][0][0][x] = self.decay(top[0].data[0][0][0][x])

    def backward(self, top, propagate_down, bottom):
        pass

    def reshape(self, bottom, top):
        top[0].reshape(*bottom[0].data.shape)

    def decay(self, x):
        x = x/2
        if x < 0.1:
            x = 0
        return x
