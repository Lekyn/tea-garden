import unittest
import genetics
import tako
from textwrap import dedent
import os
import caffe

#tests that weight genes read and mutate properly
class testWeight(unittest.TestCase):

    def setUp(self):
        self.active_list = {"testa": 6, "testb": 3}
        self.unread_a = genetics.weight_gene(1, False, False, 0, "asld",
                                             0.00, 0, 0, "nonexistant", "none")
        self.unread_b = genetics.weight_gene(1, False, False, 0, "asld",
                                             0.00, 6, 0, "testa", "testb")
        self.low_dom_a = genetics.weight_gene(1, False, False, 0, "asld",
                                             0.00, 3, 0, "testa", "testb")
        self.low_dom_b = genetics.weight_gene(1, False, False, 0, "asld",
                                             5.00, 3, 0, "testa", "testb")
        self.high_dom = genetics.weight_gene(5, False, False, 0, "asld",
                                             3.00, 3, 0, "testa", "testb")
        self.other_weight = genetics.weight_gene(5, False, False, 0, "asld",
                                             3.00, 5, 0, "testa", "testb")
        self.mut_weight = genetics.weight_gene(1, True, False, 300, "asld",
                                              3.00, 5, 0, "testa", "testb")
        self.mut_rate = genetics.weight_gene(1, True, False, 298, "asld",
                                            3.00, 5, 0, "testa", "testb")
        self.mut_dom = genetics.weight_gene(1, True, False, 50, "asld",
                                           3.00, 5, 0, "testa", "testb")
        genetics.random.seed("vigor")

    def test_canread(self):
        result_a = self.unread_a.can_read(self.active_list)
        self.assertFalse(result_a)
        result_b = self.unread_b.can_read(self.active_list)
        self.assertFalse(result_b)
        result_true = self.low_dom_a.can_read(self.active_list)
        self.assertTrue(result_true)

    def test_read(self):          
        #case where neither node can be read (one nonexistant input, one weight)
        test_a = self.unread_a.read(self.active_list, self.unread_b)
        self.assertEqual(test_a, None)
        #case where only *this* node can be read
        test_b = self.low_dom_a.read(self.active_list, self.unread_a)
        self.assertEqual(test_b, ["testa", 3, "testb", 0, 0.00])
        #case where only *other* node can be read
        test_c = self.unread_a.read(self.active_list, self.low_dom_a)
        self.assertEqual(test_c, ["testa", 3, "testb", 0, 0.00])
        #case where this node dominates
        test_d = self.high_dom.read(self.active_list, self.low_dom_a)
        self.assertEqual(test_d, ["testa", 3, "testb", 0, 3.00])
        #case where that node dominates
        test_e = self.low_dom_a.read(self.active_list, self.high_dom)
        self.assertEqual(test_e, ["testa", 3, "testb", 0, 3.00])
        #case where they co-dominate
        test_f = self.low_dom_a.read(self.active_list, self.low_dom_b)
        self.assertEqual(test_f, ["testa", 3, "testb", 0, 2.50])
        #case where they are both read, for different weights
        test_g = self.low_dom_a.read(self.active_list, self.other_weight)
        self.assertEqual(test_g, ["testa", 3, "testb", 0, 0.00,
                                  "testa", 5, "testb", 0, 3.00])
        #case where there is no other gene
        test_h = self.low_dom_a.read(self.active_list)
        self.assertEqual(test_h, ["testa", 3, "testb", 0, 0.00])

    def test_mutate(self):
        #first 20 random numbers(0, 300) are 280, 23, 262, 72, 153, 129
        #61, 1, 36, 62, 67, 72, 78, 298, 256, 196, 211, 205, 284, 181
        #case where mutatability is off
        test_mut_off = self.unread_a.mutate()
        self.assertEqual(test_mut_off, "")
        #case where mutability is on, dup off, but roll is higher than rate
        test_no_mut = self.mut_dom.mutate()
        self.assertEqual(test_no_mut, "")
        #case where mut is on, roll lower than rate (dom changes)
        test_dom_mut = self.mut_dom.mutate()
        self.assertEqual(test_dom_mut, "Dom, 1")
        #case where weight changes
        test_weight_mut = self.mut_weight.mutate()
        self.assertEqual(test_weight_mut, "Weight, 0.255821098441")
        #case where rate changes
        #first advance the rng until the next roll is 78
        x = 0
        while x < 3:
            genetics.random.randint(0,300)
            x +=1
        test_rate_mut = self.mut_rate.mutate()
        self.assertEqual(test_rate_mut, "Rate, 1")

#tests that layer genes read and mutate properly
class testLayer(unittest.TestCase):

    def setUp(self):
        self.active_list = {"cake": 5, "onion": 7}
        self.unread_a = genetics.layer_gene(5, False, False, 0, "askl",
                                            ["stairs"], 3, "IP")
        self.unread_b = genetics.layer_gene(5, False, False, 0, "askl",
                                            ["cake", "onion", "strata"], 3, "IP")
        self.low_dom_a = genetics.layer_gene(1, False, False, 0, "abcd",
                                             ["cake"], 4, "IP")
        self.low_dom_b = genetics.layer_gene(1, False, False, 0, "efgh",
                                             ["cake"], 1, "IP")
        self.high_dom = genetics.layer_gene(5, False, False, 0, "ijkl",
                                            ["cake"], 2, "IP")
        self.other_layer = genetics.layer_gene(3, False, False, 0, "mnop",
                                              ["onion"], 3, "IP")
        self.multiple_layer = genetics.layer_gene(3, False, False, 0, "qrst",
                                                  ["cake", "onion"], 3, "IP")
        self.no_inputs = genetics.layer_gene(3, False, False, 0, "uvwx",
                                             [], 3, "input")
        self.mut_rate = genetics.layer_gene(3, True, False, 270, "askl",
                                            [], 3, "input")
        self.mut_dom = genetics.layer_gene(3, True, False, 300, "askl",
                                          [], 3, "input")
        self.mut_num = genetics.layer_gene(3, True, False, 300, "askl",
                                           [], 5, "input")
        self.mut_dup = genetics.layer_gene(3, True, True, 300, "askl",
                                            [], 5, "input")
        self.mut_add_input = genetics.layer_gene(3, True, False, 300, "askl",
                                                [], 5, "")
        self.data = genetics.layer_gene(5, False, False, 0, "data",
                                        [], 9, "input")
        self.reward = genetics.layer_gene(5, False, False, 0, "reward",
                                         [], 6, "input")
        self.stm_input = genetics.layer_gene(5, False, False, 0, "stm_input",
                                             ["data", "reward"], 6, "input")
        self.stm = genetics.layer_gene(5, False, False, 0, "STM",
                                       ["stm_input"], 6, "STMlayer")
        self.concat = genetics.layer_gene(5, False, False, 0, "concat_0",
                                          ["data", "STM"], None, "concat")
        self.action = genetics.layer_gene(5, False, False, 0, "action",
                                          ["concat_0"], 6, "IP")
        self.loss = genetics.layer_gene(5, False, False, 0, "loss",
                                        ["action", "reward"], 5, "loss")

    def test_makestring(self):
        test_data = dedent("""\
                            input: \"data\"
                            input_shape: {
                              dim: 1
                              dim: 1
                              dim: 1
                              dim: 9
                            }
                            """)
        self.assertEqual(test_data, self.data.read_out())
        test_reward = dedent("""\
                        input: "reward"
                        input_shape: {
                          dim: 1
                          dim: 1
                          dim: 1
                          dim: 6
                        }
                        """)
        self.assertEqual(test_reward, self.reward.read_out())
        test_stm_input = dedent("""\
                        input: "stm_input"
                        input_shape: {
                          dim: 1
                          dim: 1
                          dim: 1
                          dim: 6
                        }
                        """)
        self.assertEqual(test_stm_input, self.stm_input.read_out())
        test_stm = dedent('''\
                    layer {
                      name: "STM"
                      type: "Python"
                      bottom: "stm_input"
                      top: "STM"
                      python_param {
                        module: "tako"
                        layer: "STMlayer"
                      }
                    }
                    ''')
        self.assertEqual(test_stm, self.stm.read_out())
        test_concat = dedent('''\
                        layer {
                          name: "concat_0"
                          type: "Concat"
                          bottom: "data"
                          bottom: "STM"
                          top: "concat_0"
                          concat_param {
                            axis: 3
                          }
                        }
                        ''')
        self.assertEqual(test_concat, self.concat.read_out())
        test_action = dedent('''\
                        layer {
                          name: "action"
                          type: "InnerProduct"
                          param { lr_mult: 1 decay_mult: 1}
                          param { lr_mult: 2 decay_mult: 0}
                          inner_product_param {
                            num_output: 6
                            weight_filler {
                              type: "xavier"
                            }
                            bias_filler {
                              type: "constant"
                              value: 0
                            }
                          }
                          bottom: "concat_0"
                          top: "action"
                        }
                        ''')
        self.assertEqual(test_action, self.action.read_out())
        test_loss = dedent('''\
                            layer {
                              name: "loss"
                              type: "EuclideanLoss"
                              bottom: "action"
                              bottom: "reward"
                              top: "loss"
                            }
                            ''')
        self.assertEqual(test_loss, self.loss.read_out())

    def test_concats(self):
        concatts = {}
        active_list = {"data": 8, "STM": 5}
        self.concat.concats(concatts, active_list)
        self.assertEqual(concatts, {"STM": ["concat_0", 8]})
        active_list["concat_0"] = 5
        self.action.concats(concatts, active_list)
        self.assertEqual(concatts, {"STM": ["concat_0", 8, "action"]})
        
    def test_read(self):
        genetics.random.seed("layers")
        concat_dict = {}
        #a case where neither is read
        test_a = self.unread_a.read("temp_file.txt", self.active_list,
                                    concat_dict, self.unread_b)
        self.assertEqual(test_a, self.active_list, concat_dict, )
        #a case where the first is read
        test_b = self.low_dom_a.read("temp_file.txt", self.active_list,
                                     concat_dict, self.unread_a)
        self.assertEqual(test_b, {"cake": 5, "onion": 7, "abcd": 4})
        #a case where the second is read
        test_c = self.unread_a.read("temp_file.txt", self.active_list,
                                    concat_dict, self.low_dom_a)
        self.assertEqual(test_c, {"cake": 5, "onion": 7, "abcd": 4})
        #a case where they have the same dom
        test_d = self.low_dom_a.read("temp_file.txt", self.active_list,
                                     concat_dict, self.low_dom_b)
        self.assertEqual(test_d, {"cake": 5, "onion": 7, "abcd": 4})
        #a case where the first dominates
        test_e = self.high_dom.read("temp_file.txt", self.active_list,
                                    concat_dict, self.low_dom_a)
        self.assertEqual(test_e, {"cake": 5, "onion": 7, "ijkl": 2})
        #a case where the second dominates
        test_f = self.low_dom_b.read("temp_file.txt", self.active_list,
                                     concat_dict, self.high_dom)
        self.assertEqual(test_f, {"cake": 5, "onion": 7, "ijkl": 2})
        #a case with no other gene (and two dependencies)
        test_g = self.multiple_layer.read("temp_file.txt", self.active_list,
                                          concat_dict)
        self.assertEqual(test_g, {"cake": 5, "onion": 7, "qrst": 3})
        #a case with no other gene (and no dependencies)
        test_h = self.no_inputs.read("temp_file.txt", self.active_list,
                                     concat_dict)
        self.assertEqual(test_h, {"cake": 5, "onion": 7, "uvwx": 3})
        #a case where the other gene has no dependencies
        test_i = self.low_dom_a.read("temp_file.txt", self.active_list,
                                     concat_dict, self.no_inputs)
        self.assertEqual(test_i, {"cake": 5, "onion": 7, "uvwx": 3})
        
        test_list  = {}
        concat_dict = {}
        test_list = self.data.read("testing alife.txt", test_list, concat_dict, None)
        test_list = self.reward.read("testing alife.txt", test_list, concat_dict, None)
        test_list = self.stm_input.read("testing alife.txt", test_list, concat_dict, None)
        test_list = self.stm.read("testing alife.txt", test_list, concat_dict, None)
        test_list = self.concat.read("testing alife.txt", test_list, concat_dict, None)
        test_list = self.action.read("testing alife.txt", test_list, concat_dict, None)
        test_list = self.loss.read("testing alife.txt", test_list, concat_dict, None)

        with open('testing alife.txt', 'r') as test_file:
            with open('alife.text', 'r') as orig_file:
                for line1, line2 in zip(test_file, orig_file):
                    self.assertEqual(line1, line2)

        os.remove("temp_file.txt")
        os.remove("testing alife.txt")
        
    def test_mutate(self):
        genetics.random.seed("vigor")
        #first 20 random numbers(0, 300) are 280, 23, 262, 72, 153, 129
        #61, 1, 36, 62, 67, 72, 78, 298, 256, 196, 211, 205, 284, 181
        test_mut_off = self.unread_a.mutate()
        self.assertEqual(test_mut_off, "")
        test_mut_dom = self.mut_dom.mutate()
        self.assertEqual(test_mut_dom, "Dom, -1")
        #next roll is 61, reset and advance rng (next roll = 153)
        genetics.random.seed("vigor")
        i = 0
        while i != 4:
            genetics.random.randint(0, 300)
            i += 1
        test_mut_rate = self.mut_rate.mutate()
        self.assertEqual(test_mut_rate, "Rate, 1")
        #advance rng to spot I want it (next roll = 196)
        i = 0
        while i != 9:
            genetics.random.randint(0, 300)
            i += 1
        test_mut_num = self.mut_num.mutate()
        self.assertEqual(test_mut_num, "Nodes, -2")
        #reset rng again (next roll = 256)
        genetics.random.seed("vigor")
        i = 0
        while i != 13:
            genetics.random.randint(0, 300)
            i += 1
        test_mut_dup = self.mut_dup.mutate()
        self.assertEqual(test_mut_dup, "Duplicate,")
        genetics.random.seed("vigor")
        genetics.random.randint(0, 300)
        test_mut_input = self.mut_add_input.mutate()
        self.assertEqual(test_mut_input, "Add input,")        

#tests that genome builds a new creature properly
#along with tests for helper functions
class testBuild(unittest.TestCase):

    def setUp(self):
        self.active_list = {"data": 8, "concat_0": 5}
        unread_a = genetics.weight_gene(1, False, False, 0, "asld",
                                             0.00, 0, 0, "nonexistant", "none")
        unread_b = genetics.weight_gene(1, False, False, 0, "asld",
                                             0.00, 0, 0, "testa", "testb")
        low_dom_a = genetics.weight_gene(1, False, False, 0, "abcd",
                                             0.00, 0, 0, "data", "action")
        low_dom_b = genetics.weight_gene(1, False, False, 0, "lowdb",
                                             5.00, 0, 0, "data", "action")
        low_dom_c = genetics.weight_gene(1, False, False, 0, "jklm",
                                             7.00, 0, 1, "data", "action")
        low_dom_d = genetics.weight_gene(1, False, False, 0, "lowdd",
                                             1.00, 4, 0, "data", "action")
        high_dom = genetics.weight_gene(5, False, False, 0, "xyz",
                                             3.00, 4, 0, "data", "action")
        other_weight = genetics.weight_gene(5, False, False, 0, "other",
                                             3.00, 4, 4, "data", "action")
        #case where neither read, both read (same gene)
        #a is read first, low_dom_d and high_dom both read
        #other_weight is left to read on b
        alist = [unread_a, low_dom_a, low_dom_c, high_dom]
        blist = [unread_b, low_dom_b, low_dom_d, other_weight]

        l_unread_a = genetics.layer_gene(5, False, False, 0, "askl",
                                            ["stairs"], 3, "IP")
        l_unread_b = genetics.layer_gene(5, False, False, 0, "askl",
                                            ["cake", "onion", "strata"], 3, "IP")
        l_low_dom_a = genetics.layer_gene(1, False, False, 0, "data",
                                             [], 8, "input")
        l_low_dom_b = genetics.layer_gene(1, False, False, 0, "efgh",
                                             [], 5, "input")
        l_low_dom_c = genetics.layer_gene(1, False, False, 0, "qrst",
                                          [], 4, "input")
        l_low_dom_d = genetics.layer_gene(1, False, False, 0, "uvwx",
                                          [], 5, "input")
        l_high_dom = genetics.layer_gene(5, False, False, 0, "ijkl",
                                            [], 2, "input")
        l_dummy_layer = genetics.layer_gene(5, False, False, 0, "blegh",
                                            [], 5, "input")
        l_concat_layer = genetics.layer_gene(5, False, False, 0, "concat_0",
                                             ["data", "blegh"], None, "concat")
        l_action_layer = genetics.layer_gene(3, False, False, 0, "action",
                                              ["concat_0"], 5, "IP")
        #case where neither read, both readable(rng set to read a)
        #a can be read, b can be read,
        #a has dom, a is longer by three genes
        clist = [l_unread_a, l_low_dom_a, l_low_dom_c, l_unread_b,
                 l_high_dom, l_dummy_layer, l_concat_layer, l_action_layer]
        dlist = [l_unread_b, l_low_dom_b, l_unread_a, l_low_dom_d, l_low_dom_b]
        
        self.test_genome_a = genetics.genome(clist, dlist, alist, blist)
        self.data = genetics.layer_gene(5, False, False, 0, "data",
                                        [], 9, "input")
        self.reward = genetics.layer_gene(5, False, False, 0, "reward",
                                         [], 6, "input")
        self.stm_input = genetics.layer_gene(5, False, False, 0, "stm_input",
                                             ["data", "reward"], 6, "input")
        self.stm = genetics.layer_gene(5, False, False, 0, "STM",
                                       ["stm_input"], 6, "STMlayer")
        self.concat = genetics.layer_gene(5, False, False, 0, "concat_0",
                                          ["data", "STM"], None, "concat")
        self.action = genetics.layer_gene(5, False, False, 0, "action",
                                          ["concat_0"], 6, "IP")
        self.loss = genetics.layer_gene(5, False, False, 0, "loss",
                                        ["action", "reward"], 6, "loss")      

    def test_gen_ident(self):
        genetics.random.seed("genetic")
        ident = genetics.genome.generate_ident()
        self.assertEqual(ident, "T780-898-895")

    def test_adjust_weights(self):
        tak = tako.Tako(0, 0, 0, None, 'alife', [])
        net = tak.solver.net
        self.assertNotEqual(tak.solver.net.params["action"][0].data[0][0], -0.06807647)
        val0 = ["data", 0, "action", 0, -0.06807647]
        genetics.genome.adjust_weight(net, val0)
        self.assertAlmostEqual(tak.solver.net.params["action"][0].data[0][0],
                               -0.06807647)
        val1 = ["data", 1, "action", 0, -0.08293831,
                "data", 2, "action", 0, -0.3910988]
        self.assertNotEqual(net.params["action"][0].data[0][1], -0.08293831)
        self.assertNotEqual(net.params["action"][0].data[0][2], -0.3910988)
        genetics.genome.adjust_weight(net, val1)
        self.assertAlmostEqual(tak.solver.net.params["action"][0].data[0][1],
                               -0.08293831)
        self.assertAlmostEqual(tak.solver.net.params["action"][0].data[0][2],
                              -0.3910988)

    def test_read_through(self):
        tak = tako.Tako(0, 0, 0, None, 'alife', [])
        net = tak.solver.net
        #case where gene is not read
        n, a = self.test_genome_a.read_through("a", 0, [], net)
        self.assertEqual(n, 1)
        self.assertEqual(a.ident, "abcd")
        #case where gene is read
        self.assertNotEqual(net.params["action"][0].data[0][3], 0.00)
        active_list = {"data": 8, "action": 5}
        n, a = self.test_genome_a.read_through("a", 1, active_list, net)
        self.assertAlmostEqual(net.params["action"][0].data[0][0], 0.00)
        self.assertEqual(n, 2)
        self.assertEqual(a.ident, "jklm")
        #case where gene is last on chromosome
        self.assertNotEqual(net.params["action"][0].data[0][4], 3.00)
        n, a = self.test_genome_a.read_through("a", 3, active_list, net)
        self.assertAlmostEqual(net.params["action"][0].data[0][4], 3.00)
        self.assertEqual(n, 4)
        self.assertEqual(a.ident, "xyz")

    def test_concats(self):
        a_u_00 = genetics.weight_gene(5, False, False, 0, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        a_o_00 = genetics.weight_gene(5, False, False, 0, "ao00",
                                      3.00, 0, 0, "INa", "IPo")
        i_u_00 = genetics.weight_gene(5, False, False, 0, "iu00",
                                      5.00, 0, 0, "INi", "IPu")
        i_o_00 = genetics.weight_gene(5, False, False, 0, "io00",
                                      5.00, 0, 0, "INi", "IPo")
        weight_list = [a_u_00, a_o_00, i_u_00, i_o_00]
        concat_genome = genetics.genome([], [], weight_list, weight_list)
        active_list = {"INa": 5, "INi": 5, "concat": 10, "IPu": 5, "IPo": 5}
        concat_dict = {"INi": ["concat", 5, "IPu", "IPo"]}
        concat_genome.concats(active_list, concat_dict)
        cwa = concat_genome.weightchr_a
        cwb = concat_genome.weightchr_b
        self.assertEqual(cwa[0].alt_in, 0)
        self.assertEqual(cwa[1].alt_in, 0)
        self.assertEqual(cwa[2].alt_in, 5)
        self.assertEqual(cwa[3].alt_in, 5)
        self.assertEqual(cwb[0].alt_in, 0)
        self.assertEqual(cwb[1].alt_in, 0)
        self.assertEqual(cwb[2].alt_in, 5)
        self.assertEqual(cwb[3].alt_in, 5)
        #test with two inputs
        e_u_00 = genetics.weight_gene(5, False, False, 0, "ie00",
                                      3.00, 0, 0, "INe", "IPu")
        e_o_00 = genetics.weight_gene(5, False, False, 0, "ie00",
                                      3.00, 0, 0, "INe", "IPo")
        weight_list2 = [a_u_00, a_o_00, i_u_00, i_o_00, e_u_00, e_o_00]
        for weight in weight_list2:
            weight.alt_in = weight.in_node
        concat_genome2 = genetics.genome([], [], weight_list2, weight_list2)
        active_list2 = {"INa": 5, "INi": 5, "INe": 5, "concat": 10, "IPu": 5,
                        "IPo": 5}
        concat_dict2 = {"INi": ["concat", 5, "IPu", "IPo"],
                        "INe": ["concat", 5, "IPu", "IPo"]}
        concat_genome2.concats(active_list2, concat_dict2)
        cwa = concat_genome2.weightchr_a
        cwb = concat_genome2.weightchr_b
        self.assertEqual(cwa[0].alt_in, 0)
        self.assertEqual(cwa[1].alt_in, 0)
        self.assertEqual(cwa[2].alt_in, 5)
        self.assertEqual(cwa[3].alt_in, 5)
        self.assertEqual(cwb[0].alt_in, 0)
        self.assertEqual(cwb[1].alt_in, 0)
        self.assertEqual(cwb[2].alt_in, 5)
        self.assertEqual(cwb[3].alt_in, 5)
        
    def test_build_weights(self):
        tak = tako.Tako(0, 0, 0, None, 'alife', [])
        net = tak.solver.net
        data = net.params["action"][0].data
        active_list = {"data": 8, "action": 5}
        #simple test
        zz_genea = genetics.weight_gene(1, False, False, 0, "zzga",
                                             1.00, 0, 0, "data", "action")
        zz_geneb = genetics.weight_gene(1, False, False, 0, "zzgb",
                                             5.00, 0, 0, "data", "action")
        zo_genea = genetics.weight_gene(1, False, False, 0, "abcd",
                                             1.00, 0, 1, "data", "action")
        zo_geneb = genetics.weight_gene(1, False, False, 0, "abcd",
                                             5.00, 0, 1, "data", "action")
        genome_a = genetics.genome([], [], [zz_genea, zo_genea], [zz_geneb,
                                                                    zo_geneb])
        genome_a.build_weights(active_list, net)
        self.assertAlmostEqual(data[0][0], 3.00)
        self.assertAlmostEqual(data[1][0], 3.00)
        #test where a is one longer
        zt_genea = genetics.weight_gene(1, False, False, 0, "abcd",
                                        1.00, 0, 2, "data", "action")
        genome_b = genetics.genome([], [], [zz_genea, zo_genea, zt_genea],
                    [zz_geneb, zo_geneb])
        genome_b.build_weights(active_list, net)
        self.assertAlmostEqual(data[2][0], 1.00)
        #test where b is one longer
        zt_geneb = genetics.weight_gene(1, False, False, 0, "abcd",
                                        5.00, 0, 2, "data", "action")
        genome_c = genetics.genome([], [], [zz_genea, zo_genea],
                    [zz_geneb, zo_geneb, zt_geneb])
        genome_c.build_weights(active_list, net)
        self.assertAlmostEqual(data[2][0], 5.00)
        #test where a pulls ahead
        oz_genea = genetics.weight_gene(1, False, False, 0, "efgh",
                                        1.00, 1, 0, "data", "action")
        genome_d = genetics.genome([], [], [zz_genea, oz_genea],
                                   [zz_geneb, zo_geneb])
        genome_d.build_weights(active_list, net)
        self.assertAlmostEqual(data[0][1], 1.00)
        #test where b pulls ahead
        oz_geneb = genetics.weight_gene(1, False, False, 0, "ijkl",
                                        5.00, 1, 0, "data", "action")
        genome_e = genetics.genome([], [], [zz_genea, zo_genea],
                                   [zz_geneb, oz_geneb])
        genome_e.build_weights(active_list, net)
        self.assertAlmostEqual(data[0][1], 5.00)
        #test where a out gets bigger than b out
        genome_f = genetics.genome([], [], [zo_genea, zz_genea, zt_genea],
                                   [zo_geneb, zt_geneb, zz_geneb])
        genome_f.build_weights(active_list, net)
        self.assertAlmostEqual(data[0][0], 3.00)
        data[0][0] = 7.00
        #test where b out gets bigger than a out
        genome_g = genetics.genome([], [], [zo_genea, zt_geneb, zz_genea],
                                   [zo_geneb, zz_geneb, zt_geneb])
        genome_g.build_weights(active_list, net)
        self.assertAlmostEqual(data[0][0], 3.00)
        data[0][0] = 7.00
        ###Note to self: add one that doesn't have a 0/0 - h, i
        #test where a goes to 0/0 while b is still going
        ff_genea = genetics.weight_gene(1, False, False, 0, "ffga",
                                        1.00, 5, 4, "data", "action")
        ff_geneb = genetics.weight_gene(1, False, False, 0, "ffgb",
                                        5.00, 5, 4, "data", "action")
        sz_geneb = genetics.weight_gene(1, False, False, 0, "szgb",
                                        5.00, 6, 0, "data", "action")
        so_geneb = genetics.weight_gene(1, False, False, 0, "sogb",
                                        5.00, 6, 1, "data", "action")
        genome_j = genetics.genome([], [], [ff_genea, zz_genea],
                                   [ff_geneb, sz_geneb, so_geneb, zz_geneb])
        genome_j.build_weights(active_list, net)
        self.assertAlmostEqual(data[0][0], 3.00)
        #test where b goes to 0/0 while a is still going
        data[0][0] = 7.00
        sz_genea = genetics.weight_gene(1, False, False, 0, "szga",
                                        1.00, 6, 0, "data", "action")
        so_genea = genetics.weight_gene(1, False, False, 0, "szga",
                                        1.00, 6, 1, "data", "action")
        genome_l = genetics.genome([], [], [ff_genea, sz_genea, so_genea, zz_genea],
                                   [ff_geneb, zz_geneb])
        genome_l.build_weights(active_list, net)
        self.assertAlmostEqual(data[0][0], 3.00)
   
    def test_build(self):
        genetics.random.seed("genetic")
        tak = self.test_genome_a.build(0, 0, 0)
        x = os.path.join('Gen files', 'T780-898-895.gen')
        os.remove(x)
        data = tak.solver.net.params['action'][0].data
        self.assertAlmostEqual(data[0][0], 2.50)
        self.assertAlmostEqual(data[1][0], 7.00)
        self.assertAlmostEqual(data[0][4], 3.00)
        self.assertAlmostEqual(data[4][4], 3.00)
        #test concats
        layer_a = genetics.layer_gene(5, False, False, 0, "INa",
                                        [], 5, "input")
        layer_i = genetics.layer_gene(5, False, False, 0, "INi",
                                        [], 5, "input")
        layer_concat = genetics.layer_gene(5, False, False, 0, "concat",
                                        ["INa", "INi"], None, "concat")
        layer_u = genetics.layer_gene(5, False, False, 0, "IPu",
                                        ["concat"], 5, "IP")
        layer_o = genetics.layer_gene(5, False, False, 0, "IPo",
                                        ["concat"], 5, "IP")
        layer_list = [layer_a, layer_i, layer_concat, layer_u, layer_o]
        a_u_00 = genetics.weight_gene(5, False, False, 0, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        a_o_00 = genetics.weight_gene(5, False, False, 0, "ao00",
                                      3.00, 0, 0, "INa", "IPo")
        i_u_00 = genetics.weight_gene(5, False, False, 0, "iu00",
                                      5.00, 0, 0, "INi", "IPu")
        i_o_00 = genetics.weight_gene(5, False, False, 0, "io00",
                                      5.00, 0, 0, "INi", "IPo")
        weight_list = [a_u_00, a_o_00, i_u_00, i_o_00]
        concat_genome = genetics.genome(layer_list, layer_list, weight_list,
                                        weight_list)
        tak = concat_genome.build(0, 0, 0)
        data_u = tak.solver.net.params['IPu'][0].data
        data_o = tak.solver.net.params['IPo'][0].data        
        x = os.path.join('Gen files', 'T431-739-965.gen')
        os.remove(x)
        self.assertAlmostEqual(data_u[0][0], 3.00)
        self.assertAlmostEqual(data_u[0][5], 5.00)
        self.assertAlmostEqual(data_o[0][0], 3.00)
        self.assertAlmostEqual(data_o[0][5], 5.00)
        #default genome; this needs to work!
        layers = [self.data, self.reward, self.stm_input, self.stm,
                  self.concat, self.action, self.loss]
        weights = []
        with open("default weights.txt") as f:
            for n in range(6):
                for m in range(15):
                    x = f.readline()
                    x = float(x[0:-1])
                    iden = str(n) + " " + str(m)
                    if m < 9:
                        in_layer = "data"
                        m_adj = m
                    else:
                        in_layer = "STM"
                        m_adj = m - 9
                    w = genetics.weight_gene(5, False, False, 0, iden,
                                             x, m_adj, n, in_layer, "action")
                    weights.append(w)
        default_genome = genetics.genome(layers, layers, weights, weights)
        test_default = caffe.Net('alife.text', 'test default genome.txt', caffe.TRAIN)
        default_tak = default_genome.build(0, 0, 0)
        x = os.path.join('Gen files', 'T994-256-674.gen')
        os.remove(x)
        n = 0
        m = 0
        test_data = test_default.params['action'][0].data
        default_data = default_tak.solver.net.params['action'][0].data
        for n in range(6):
            for m in range(15):
                self.assertAlmostEqual(test_data[n][m], default_data[n][m])

#tests the genome mutation functions
class testMutation(unittest.TestCase):

    def setUp(self):
        genetics.random.seed("vigor")

    def test_new_ident(self):
        ident = genetics.genome.new_ident()
        self.assertEqual(ident, "YCWGNL")

    def test_new_input(self):
        test_layer_b = genetics.layer_gene(4, True, True, 3, "INa",
                                        [], 5, "IP")
        test_dup_layer = genetics.layer_gene(4, True, True, 3, "ABCDEF",
                                             [], 5, "IP")
        test_genome = genetics.genome([test_dup_layer, test_layer_b], [test_layer_b],
                                      [],[])
        x = test_genome.new_input(test_genome.layerchr_a[0], test_genome.layerchr_a)
        self.assertEqual(x.ident, "INa")
        #test with multiple possible layers
        test_layer_c = genetics.layer_gene(4, True, True, 3, "INi",
                                        [], 5, "IP")
        test_layer_d = genetics.layer_gene(4, True, True, 3, "INu",
                                        [], 5, "IP")
        test_genome_b = genetics.genome([test_layer_b, test_layer_c, test_layer_d],
                                        [test_dup_layer, test_layer_b, test_layer_c,
                                         test_layer_d], [], [])
        x = test_genome_b.new_input(test_genome_b.layerchr_b[0], test_genome_b.layerchr_b)
        self.assertEqual("INa", x.ident)
        #test with concats and loss layer at end
        test_concat_layer = genetics.layer_gene(4, True, True, 3, "conc", [], 5, "concat")
        test_loss_layer = genetics.layer_gene(4, True, True, 3, "loss", [], 5, "loss")
        test_genome_c = genetics.genome([test_layer_b, test_concat_layer, test_loss_layer],
                                        [test_dup_layer, test_layer_b, test_concat_layer,
                                         test_loss_layer], [], [])
        x = test_genome_c.new_input(test_genome_c.layerchr_b[0], test_genome_c.layerchr_b)
        self.assertEqual(x.ident, "INa")

    def test_find_n_inputs(self):
        #single input
        test_in = genetics.layer_gene(1, False, False, 0, "IN", [], 5, "data")
        test_out = genetics.layer_gene(1, False, False, 0, "OUT", ["IN"], 5, "IP")
        genome = genetics.genome([test_in, test_out], [], [], [])
        n, d = genome.find_n_inputs(test_out, genome.layerchr_a)
        self.assertEqual(n, 5)
        self.assertEqual({"IN": 5}, d)
        #concat input
        test_in2 = genetics.layer_gene(1, False, False, 0, "IN2", [], 5, "data")
        test_concat = genetics.layer_gene(1, False, False, 0, "CONC",
                                          ["IN", "IN2"], None, "concat")
        test_out = genetics.layer_gene(1, False, False, 0, "OUT", ["CONC"], 5, "IP")
        genome2 = genetics.genome([test_in, test_in2, test_concat, test_out],
                                  [], [], [])
        n, d = genome.find_n_inputs(test_out, genome2.layerchr_a)
        self.assertEqual(n, 10)
        self.assertEqual({"IN": 5, "IN2": 5}, d)

    def test_dup_weights(self):
        #simplest test case
        test_in = genetics.layer_gene(4, False, False, 0, "IN", [], 1, "data")
        test_layer_b = genetics.layer_gene(4, True, True, 3, "OUT",
                                        ["ABCDEF"], 5, "IP")
        test_dup_layer = genetics.layer_gene(4, True, True, 3, "ABCDEF",
                                             ["IN"], 5, "IP")
        test_genome = genetics.genome([test_in, test_dup_layer, test_layer_b], [],
                                      [], [])
        test_genome.dup_weights(test_dup_layer, test_layer_b, test_genome.layerchr_a)
        self.assertEqual(len(test_genome.weightchr_a), 30)
        n = 0
        m = 0
        o = 0
        for g in test_genome.weightchr_a:
            self.assertEqual(g.in_node, m)
            self.assertEqual(g.out_node, n)
            if o == 1:
                self.assertEqual(g.in_layer, "ABCDEF")
                self.assertEqual(g.out_layer, "OUT")
            else:
                self.assertEqual(g.in_layer, "IN")
                self.assertEqual(g.out_layer, "ABCDEF")
            n += 1
            if o == 0 and n == 5:
                o = 1
                n = 0
            else:
                if n == 5:
                    n = 0
                    m += 1
        #now a case where the input is a concat, as it should be
        test_layer_b.inputs = ["concat"]
        concat = genetics.layer_gene(5, False, False, 0, "concat", ["IN", "ABCDEF"],
                                     None, "concat")
        test_genome2 = genetics.genome([test_in, test_dup_layer, concat, test_layer_b],
                                       [], [], [])
        test_genome2.dup_weights(test_dup_layer, test_layer_b, test_genome2.layerchr_a)
        self.assertEqual(len(test_genome2.weightchr_a), 30)
        n = 0
        m = 0
        o = 0
        for g in test_genome2.weightchr_a:
            self.assertEqual(g.in_node, m)
            self.assertEqual(g.out_node, n)
            if o == 1:
                self.assertEqual(g.in_layer, "ABCDEF")
                self.assertEqual(g.out_layer, "OUT")
            else:
                self.assertEqual(g.in_layer, "IN")
                self.assertEqual(g.out_layer, "ABCDEF")
            n += 1
            if o == 0 and n == 5:
                o = 1
                n = 0
            else:
                if n == 5:
                    n = 0
                    m += 1
        
    def test_add_concats(self):
        #case where input wasn't concat
        input_layer = genetics.layer_gene(4, True, True, 3, "input",
                                        [], 5, "data")
        new_layer = genetics.layer_gene(4, True, True, 3, "new",
                                        ["input"], 5, "IP")
        old_layer = genetics.layer_gene(4, True, True, 3, "old",
                                        ["input"], 5, "IP")
        gen = genetics.genome([input_layer, new_layer, old_layer], [], [], [])
        gen.add_concats(gen.layerchr_a[1], gen.layerchr_a[2], gen.layerchr_a)
        self.assertEqual(len(gen.layerchr_a), 4)
        self.assertEqual(gen.layerchr_a[2].layer_type, "concat")
        #case where the input is a concat and not shared
        old_layer = genetics.layer_gene(4, True, True, 3, "old",
                                        ["concat"], 5, "IP")
        input_layer_2 = genetics.layer_gene(4, True, True, 3, "input2",
                                        [], 5, "data")
        conc_layer = genetics.layer_gene(4, True, True, 3, "concat",
                                        ["input", "input2"], None, "concat")
        gen2 = genetics.genome([input_layer, input_layer_2, conc_layer, new_layer,
                                old_layer], [], [], [])
        gen2.add_concats(gen2.layerchr_a[3], gen2.layerchr_a[4], gen2.layerchr_a)
        self.assertEqual(len(gen2.layerchr_a), 5)
        self.assertEqual(gen2.layerchr_a[3].layer_type, "concat")
        self.assertEqual(len(gen2.layerchr_a[3].inputs), 3)
        self.assertNotEqual(gen2.layerchr_a[4].inputs[0], "concat")
        #case where the input is a concat and is shared
        old_layer = genetics.layer_gene(4, True, True, 3, "old",
                                        ["concat"], 5, "IP")
        other_layer = genetics.layer_gene(4, True, True, 3, "old2",
                                        ["concat"], 5, "IP")
        conc_layer = genetics.layer_gene(4, True, True, 3, "concat",
                                        ["input", "input2"], None, "concat")
        gen3 = genetics.genome([input_layer, input_layer_2, conc_layer, new_layer,
                                old_layer, other_layer], [], [], [])
        gen3.add_concats(gen3.layerchr_a[3], gen3.layerchr_a[4], gen3.layerchr_a)
        self.assertEqual(len(gen3.layerchr_a), 7)
        self.assertEqual(gen3.layerchr_a[4].layer_type, "concat")
        self.assertEqual(len(gen3.layerchr_a[4].inputs), 2)
        self.assertNotEqual(gen3.layerchr_a[4].ident, "concat")
        self.assertNotEqual(gen3.layerchr_a[5].inputs[0], "concat")

    def test_handle_duplication(self):
        test_input = genetics.layer_gene(4, False, False, 0, "d", [], 1, "data")
        test_layer_b = genetics.layer_gene(4, True, True, 3, "INa",
                                        ["d"], 5, "IP")
        test_genome = genetics.genome([test_input, test_layer_b], [],
                                      [], [])
        test_genome.handle_duplication(test_layer_b, test_genome.layerchr_a)
        self.assertEqual(len(test_genome.layerchr_a), 4)
        self.assertNotEqual(test_genome.layerchr_a[1].ident, "INa")
        self.assertEqual(len(test_genome.weightchr_a), 30)
        self.assertEqual(len(test_genome.weightchr_b), 30)
        i = 0
        j = 0
        k = 0
        for gene in test_genome.weightchr_a:
            if k == 0:
                self.assertEqual(gene.in_layer, "d")
            else:
                self.assertEqual(gene.out_layer, "INa")
            self.assertEqual(gene.out_node, i)
            self.assertEqual(gene.in_node, j)
            i += 1
            if i > 4:
                i = 0
                if k == 0:
                    k = 1
                else:
                    j += 1

    def test_find_outputs(self):
        #simple case
        test_in = genetics.layer_gene(5, False, False, 0, "d", [], 1, "data")
        test_gene = genetics.layer_gene(5, True, True, 5, "tester", ["d"], 5, "IP")
        test_genome = genetics.genome([test_in, test_gene], [], [], [])
        out = test_genome.find_outputs(test_in, test_genome.layerchr_a)
        self.assertEqual(out, [test_gene])
        #case with 3 outputs across two concats
        conc1 = genetics.layer_gene(5, False, False, 0, "con1", ["tester"],
                                    None, "concat")
        conc2 = genetics.layer_gene(5, False, False, 0, "con2", ["tester", "d"],
                                    None, "concat")
        out1 = genetics.layer_gene(5, True, True, 5, "out1", ["con1"], 5, "IP")
        out2 = genetics.layer_gene(5, True, True, 5, "out2", ["con2"], 3, "IP")
        out3 = genetics.layer_gene(5, True, True, 5, "out3", ["con2"], 6, "IP")
        test_genome2 = genetics.genome([test_in, test_gene, conc1, conc2, out1,
                                        out2, out3], [], [], [])
        out = test_genome2.find_outputs(test_gene, test_genome2.layerchr_a)
        self.assertEqual(out, [out1, out2, out3])

    def test_add_nodes(self):
        test_in = genetics.layer_gene(5, False, False, 0, "d", [], 1, "data")
        test_gene = genetics.layer_gene(5, True, True, 5, "tester", ["d"], 5, "IP")
        test_out = genetics.layer_gene(5, False, False, 0, "o", ["tester"], 3, "IP")
        weights = []
        for i in range(5):
            w = genetics.weight_gene(5, True, False, 3, str(i), 3, 0, i, "d",
                                     "tester")
            weights.append(w)
        for i in range(5):
            for j in range (3):
                w = genetics.weight_gene(5, True, False, 3, str(i), 3,
                                         i, j, "tester", "o")
                weights.append(w)
        test_genome = genetics.genome([test_in, test_gene, test_out], [],
                                      weights, [])
        
        n_in, d = test_genome.find_n_inputs(test_gene, test_genome.layerchr_a)
        test_genome.add_nodes(test_gene, test_genome.layerchr_a, 2,
                              test_genome.weightchr_a, n_in, d)
        #add_nodes itself no longer does this
        #self.assertEqual(test_gene.nodes, 7)
        test_gene.nodes += 2
        self.assertEqual(len(test_genome.weightchr_a), 28)
        self.assertEqual(len(test_genome.weightchr_b), 0)
        #test that inputs/outputs are right
        n = 0
        for g in test_genome.weightchr_a[:6]:
            self.assertEqual(g.out_node, n)
            n += 1
        n = 0
        m = 0
        for g in test_genome.weightchr_a[7:]:
            self.assertEqual(g.in_node, n)
            self.assertEqual(g.out_node, m)
            m += 1
            if m > 2:
                m = 0
                n += 1
        #more complicated version: 3 outputs on 2 concats, weights on both chrs
        conc1 = genetics.layer_gene(5, False, False, 0, "con1", ["tester"],
                                    None, "concat")
        conc2 = genetics.layer_gene(5, False, False, 0, "con2", ["tester", "d"],
                                    None, "concat")
        out1 = genetics.layer_gene(5, True, True, 5, "out1", ["con1"], 5, "IP")
        out2 = genetics.layer_gene(5, True, True, 5, "out2", ["con2"], 3, "IP")
        out3 = genetics.layer_gene(5, True, True, 5, "out3", ["con2"], 6, "IP")
        test_gene.nodes = 3
        weights = []
        compare_weights = []
        for i in range(4):
            w = genetics.weight_gene(5, True, False, 3, str(i), 3, 0, i, "d",
                                     "tester")
            if i < 3:
                weights.append(w)
            compare_weights.append(w)
        for i in range(4):
            for j in range(5):
                w = genetics.weight_gene(5, True, False, 3, str(i), 3,
                                         i, j, "tester", "out1")
                if i < 3:
                    weights.append(w)
                compare_weights.append(w)
        for i in range(4):
            for j in range (3):
                w = genetics.weight_gene(5, True, False, 3, str(i), 3,
                                         i, j, "tester", "out2")
                if i < 3:
                    weights.append(w)
                compare_weights.append(w)
        for i in range(4):
            for j in range (6):
                w = genetics.weight_gene(5, True, False, 3, str(i), 3,
                                         i, j, "tester", "out3")
                if i < 3:
                    weights.append(w)
                compare_weights.append(w)
        test_genome2 = genetics.genome([test_in, test_gene, conc1, conc2, out1,
                                        out2, out3], [], weights, weights)
        n_in, d = test_genome.find_n_inputs(test_gene, test_genome.layerchr_a)
        test_genome2.add_nodes(test_gene, test_genome2.layerchr_a, 1,
                               test_genome2.weightchr_a, n_in, d)
        test_genome2.add_nodes(test_gene, test_genome2.layerchr_b, 1,
                               test_genome2.weightchr_b, n_in, d)
        test_gene.nodes += 1     
        #45 original + 1 + 5 + 3 + 6 = 60
        self.assertEqual(len(test_genome2.weightchr_a), 60)
        self.assertEqual(len(test_genome2.weightchr_b), 60)
        for i in range(len(compare_weights)):
            self.assertEqual(compare_weights[i].in_node,
                             test_genome2.weightchr_a[i].in_node)
            self.assertEqual(compare_weights[i].in_node,
                             test_genome2.weightchr_b[i].in_node)
            self.assertEqual(compare_weights[i].out_node,
                             test_genome2.weightchr_a[i].out_node)
            self.assertEqual(compare_weights[i].out_node,
                             test_genome2.weightchr_b[i].out_node)
        #now a case where the layer shrank in the past, then re-expands
        test_gene.nodes -= 2
        n_in, d = test_genome.find_n_inputs(test_gene, test_genome.layerchr_a)
        test_genome2.add_nodes(test_gene, test_genome2.layerchr_a, 2,
                               test_genome2.weightchr_a, n_in, d)
        test_genome2.add_nodes(test_gene, test_genome2.layerchr_b, 2,
                               test_genome2.weightchr_b, n_in, d)
        test_gene.nodes += 2
        self.assertEqual(len(test_genome2.weightchr_a), 60)
        self.assertEqual(len(test_genome2.weightchr_b), 60)
        for i in range(len(compare_weights)):
            self.assertEqual(compare_weights[i].in_node,
                             test_genome2.weightchr_a[i].in_node)
            self.assertEqual(compare_weights[i].in_node,
                             test_genome2.weightchr_b[i].in_node)
            self.assertEqual(compare_weights[i].out_node,
                             test_genome2.weightchr_a[i].out_node)
            self.assertEqual(compare_weights[i].out_node,
                             test_genome2.weightchr_b[i].out_node)
        #and lastly a case where the layer shrank, but expanded to become
        #larger than it originally was
        test_gene.nodes -= 2
        n_in, d = test_genome.find_n_inputs(test_gene, test_genome.layerchr_a)
        test_genome2.add_nodes(test_gene, test_genome2.layerchr_a, 3,
                               test_genome2.weightchr_a, n_in, d)
        test_genome2.add_nodes(test_gene, test_genome2.layerchr_b, 3,
                               test_genome2.weightchr_b, n_in, d)
        test_gene.nodes +=3
        self.assertEqual(len(test_genome2.weightchr_a), 75)
        self.assertEqual(len(test_genome2.weightchr_b), 75)
        compare_weights = []
        for i in range(5):
            w = genetics.weight_gene(5, True, False, 3, str(i), 3, 0, i, "d",
                                     "tester")
            compare_weights.append(w)
        for i in range(5):
            for j in range(5):
                w = genetics.weight_gene(5, True, False, 3, str(i), 3,
                                         i, j, "tester", "out1")
                compare_weights.append(w)
        for i in range(5):
            for j in range (3):
                w = genetics.weight_gene(5, True, False, 3, str(i), 3,
                                         i, j, "tester", "out2")
                compare_weights.append(w)
        for i in range(5):
            for j in range (6):
                w = genetics.weight_gene(5, True, False, 3, str(i), 3,
                                         i, j, "tester", "out3")
                compare_weights.append(w)
        for i in range(len(compare_weights)):
            self.assertEqual(compare_weights[i].in_node,
                             test_genome2.weightchr_a[i].in_node)
            self.assertEqual(compare_weights[i].in_node,
                             test_genome2.weightchr_b[i].in_node)
            self.assertEqual(compare_weights[i].out_node,
                             test_genome2.weightchr_a[i].out_node)
            self.assertEqual(compare_weights[i].out_node,
                             test_genome2.weightchr_b[i].out_node)    
        
    def test_handle_mutation(self):
        test_weight_a = genetics.weight_gene(5, True, False, 0, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        test_weight_b = genetics.weight_gene(4, True, False, 300, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        test_layer_a = genetics.layer_gene(5, True, False, 0, "INa",
                                        [], 5, "input")
        test_layer_b = genetics.layer_gene(4, True, True, 3, "INa",
                                        [], 5, "IP")
        test_genome = genetics.genome([test_layer_a], [test_layer_b],
                                      [test_weight_a], [test_weight_b])
        test_genome.handle_mutation("Dom, 1", test_weight_a)
        self.assertEqual(test_weight_a.dom, 5)
        test_genome.handle_mutation("Dom, -1", test_weight_a)
        self.assertEqual(test_weight_a.dom, 4)
        test_genome.handle_mutation("Dom, 1", test_weight_b)
        self.assertEqual(test_weight_b.dom, 5)
        test_genome.handle_mutation("Weight, 3.0", test_weight_a)
        self.assertEqual(test_weight_a.weight, 6.00)
        test_genome.handle_mutation("Weight, -3.0", test_weight_b)
        self.assertEqual(test_weight_b.weight, 0.00)
        test_genome.handle_mutation("Rate, -1", test_weight_a)
        self.assertEqual(test_weight_a.mut_rate, 0)
        test_genome.handle_mutation("Rate, 1", test_weight_a)
        self.assertEqual(test_weight_a.mut_rate, 1)
        test_genome.handle_mutation("Rate, 1", test_weight_b)
        self.assertEqual(test_weight_b.mut_rate, 300)
        test_genome.handle_mutation("Rate, -1", test_weight_b)
        self.assertEqual(test_weight_b.mut_rate, 299)
        #TODO not all layer mutations are going to be implemented yet
        #in fact, right now they shouldn't be mutating at all
        #but these ones are simple enough to test at the moment
        test_genome.handle_mutation("Rate, -1", test_layer_a)
        self.assertEqual(test_layer_a.mut_rate, 0)
        test_genome.handle_mutation("Rate, 1", test_layer_a)
        self.assertEqual(test_layer_a.mut_rate, 1)
        test_genome.handle_mutation("Rate, -1", test_layer_b)
        self.assertEqual(test_layer_b.mut_rate, 2)
        test_genome.handle_mutation("Dom, 1", test_layer_a)
        self.assertEqual(test_layer_a.dom, 5)
        test_genome.handle_mutation("Dom, -1", test_layer_a)
        self.assertEqual(test_layer_a.dom, 4)
        test_genome.handle_mutation("Dom, 1", test_layer_b)
        self.assertEqual(test_layer_b.dom, 5)
        #test duplication
        test_in = genetics.layer_gene(5, False, False, 0, "d", [], 1, "data")
        test_dupl = genetics.layer_gene(5, True, True, 5, "TEST", ["d"], 5, "IP")
        test_dup = genetics.genome([], [test_in, test_dupl], [], [])
        test_dup.handle_mutation("Duplicate,", test_dup.layerchr_b[1],
                                 test_dup.layerchr_b)
        self.assertEqual(len(test_dup.layerchr_b), 4)
        self.assertEqual(len(test_dup.layerchr_b[1].inputs), 1)
        self.assertEqual(len(test_dup.layerchr_b[3].inputs), 1)
        self.assertEqual(len(test_dup.weightchr_b), 30)
        self.assertEqual(len(test_dup.weightchr_a), 30)
        #test change in node #
        #first losing nodes
        test_dup.handle_mutation("Nodes, -3", test_dup.layerchr_b[1],
                                 test_dup.layerchr_b)
        self.assertEqual(len(test_dup.weightchr_b), 30)
        self.assertEqual(test_dup.layerchr_b[1].nodes, 2)
        #now adding nodes to one that used to have them and don't need more
        test_dup.handle_mutation("Nodes, 1", test_dup.layerchr_b[1],
                                test_dup.layerchr_b)
        self.assertEqual(test_dup.layerchr_b[1].nodes, 3)
        self.assertEqual(len(test_dup.weightchr_b), 30)
        #and adding nodes to one that did not used to have them
        test_dup.handle_mutation("Nodes, 3", test_dup.layerchr_b[1],
                                test_dup.layerchr_b)
        self.assertEqual(test_dup.layerchr_b[1].nodes, 6)
        self.assertEqual(len(test_dup.weightchr_b), 36)
        #more complicated case where different numbers of weights are needed
        #for different layers
        test_dup.layerchr_b.append(genetics.layer_gene(5, False, False, 3,
                                                       "TEST2", ["YCWGNL"], 1,
                                                       "IP"))
        for i in range(7):
            test_dup.weightchr_b.append(genetics.weight_gene(5, True, True, 3,
                                                             str(i), 3, i, 0,
                                                             "YCWGNL", "TEST2"))
        test_dup.handle_mutation("Nodes, 2", test_dup.layerchr_b[1],
                                test_dup.layerchr_b)
        self.assertEqual(test_dup.layerchr_b[1].nodes, 8)
        self.assertEqual(len(test_dup.weightchr_b), 56)
        
    def test_mutate(self):
        #first 20 random numbers(0, 300) are 280, 23, 262, 72, 153, 129
        #61, 1, 36, 62, 67, 72, 78, 298, 256, 196, 211, 205, 284, 181
        #TODO layers do not mutate yet!
        wgene_0 = genetics.weight_gene(5, True, False, 300, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        wgene_1 = genetics.weight_gene(5, True, False, 300, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        wgene_2 = genetics.weight_gene(5, True, False, 50, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        wgene_3 = genetics.weight_gene(5, False, False, 300, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        wgene_4 = genetics.weight_gene(5, True, False, 100, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        wgene_5 = genetics.weight_gene(5, True, False, 100, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        test_genome = genetics.genome([],[], [wgene_0, wgene_1, wgene_2],
                                      [wgene_3, wgene_4, wgene_5])
        test_genome.mutate()
        self.assertNotEqual(wgene_0.weight, 3.00)
        self.assertNotEqual(wgene_1.weight, 3.00)
        self.assertEqual(wgene_2.weight, 3.00)
        self.assertEqual(wgene_2.dom, 5)
        self.assertEqual(wgene_2.mut_rate, 50)
        self.assertEqual(wgene_3.weight, 3.00)
        self.assertEqual(wgene_3.dom, 5)
        self.assertEqual(wgene_3.mut_rate, 300)
        self.assertNotEqual(wgene_4.weight, 3.00)
        self.assertNotEqual(wgene_5.weight, 3.00)
        

#tests recombination and helper functions
class testRecombination(unittest.TestCase):

    def setUp(self):
        genetics.random.seed("genetic")
        #simple case
        layer_a = genetics.layer_gene(5, False, False, 0, "INa",
                                        [], 5, "input")
        layer_i = genetics.layer_gene(5, False, False, 0, "INi",
                                        [], 5, "input")
        layer_concat = genetics.layer_gene(5, False, False, 0, "concat",
                                        ["INa", "INi"], None, "concat")
        layer_u = genetics.layer_gene(5, False, False, 0, "IPu",
                                        ["concat"], 5, "IP")
        layer_o = genetics.layer_gene(5, False, False, 0, "IPo",
                                        ["concat"], 5, "IP")
        layer_list_a = [layer_a, layer_i, layer_concat, layer_u, layer_o]
        layer_a2 = genetics.layer_gene(5, False, False, 0, "INa",
                                        [], 7, "input")
        layer_o2 = genetics.layer_gene(5, False, False, 0, "IPo",
                                        ["concat"], 7, "IP")
        layer_list_b = [layer_a2, layer_i, layer_concat, layer_u, layer_o2]
        a_u_00 = genetics.weight_gene(5, False, False, 0, "au00",
                                      3.00, 0, 0, "INa", "IPu")
        a_o_00 = genetics.weight_gene(5, False, False, 0, "ao00",
                                      3.00, 0, 0, "INa", "IPo")
        i_u_00 = genetics.weight_gene(5, False, False, 0, "iu00",
                                      5.00, 0, 0, "INi", "IPu")
        i_o_00 = genetics.weight_gene(5, False, False, 0, "io00",
                                      5.00, 0, 0, "INi", "IPo")
        weight_list_a = [a_u_00, a_o_00, i_u_00, i_o_00]
        a_u = genetics.weight_gene(5, False, False, 0, "au00",
                                     7.00, 0, 0, "INa", "IPu")
        i_o = genetics.weight_gene(5, False, False, 0, "io00",
                                      7.00, 0, 0, "INi", "IPo")
        weight_list_b = [a_u, a_o_00, i_u_00, i_o]
        self.genome_a = genetics.genome(layer_list_a, layer_list_b,
                                   weight_list_a, weight_list_b)
        #a case with more complicated weight genetics (extras in front) 
        a_u_01 = genetics.weight_gene(5, False, False, 0, "au01",
                                      3.00, 0, 1, "INa", "IPu")
        a_u_02 = genetics.weight_gene(5, False, False, 0, "au02",
                                      3.00, 0, 2, "INa", "IPu")
        a_u_03 = genetics.weight_gene(5, False, False, 0, "au03",
                                      3.00, 0, 3, "INa", "IPu")
        a_o_01 = genetics.weight_gene(5, False, False, 0, "ao01",
                                      3.00, 0, 3, "INa", "IPo")
        weight_list_c = [a_u_00, a_u_01, a_u_02, a_u_03, a_o_00, a_o_01, i_u_00,
                         i_o_00]
        weight_list_d = [a_u_00, a_u_01, a_o_00, a_o_01, i_u_00, i_o_00]
        self.genome_b = genetics.genome(layer_list_a, layer_list_b, weight_list_c,
                                        weight_list_d)
        #and switched around
        self.genome_c = genetics.genome(layer_list_a, layer_list_b, weight_list_d,
                                        weight_list_c)
        #case where the extras are on the end
        #and one strand gets an extra layer
        i_o_01 = genetics.weight_gene(5, False, False, 0, "io00",
                                      5.00, 0, 1, "INi", "IPo")
        i_o_02 = genetics.weight_gene(5, False, False, 0, "io00",
                                      5.00, 0, 2, "INi", "IPo")
        layer_e = genetics.layer_gene(5, False, False, 0, "IPe",
                                        ["concat"], 5, "IP")
        layer_list_c = [layer_a, layer_i, layer_concat, layer_u, layer_o, layer_e]
        weight_list_e = [a_u_00, a_u_01, a_o_00, a_o_01, i_u_00, i_o_00, i_o_01,
                         i_o_02]
        self.genome_d = genetics.genome(layer_list_c, layer_list_b, weight_list_e,
                                        weight_list_d)
        self.genome_e = genetics.genome(layer_list_a, layer_list_c, weight_list_d,
                                        weight_list_e)
        #case where the extras are in the middle
        i_u_01 = genetics.weight_gene(5, False, False, 0, "iu01",
                                      5.00, 0, 1, "INi", "IPu")
        i_u_02 = genetics.weight_gene(5, False, False, 0, "iu02",
                                      5.00, 0, 2, "INi", "IPu")
        weight_list_f = [a_u_00, a_u_01, a_o_00, a_o_01, i_u_00, i_u_01, i_u_02,
                         i_o_00]
        self.genome_f = genetics.genome(layer_list_a, layer_list_b, weight_list_f,
                                        weight_list_d)
        self.genome_g = genetics.genome(layer_list_a, layer_list_b, weight_list_d,
                                        weight_list_f)
        #case where the extras are for a different layer, at end
        other_0 = genetics.weight_gene(5, False, False, 0, "asdl",
                                      5.00, 0, 0, "asdl", "jkl;")
        other_1 = genetics.weight_gene(5, False, False, 0, "jkl;",
                                      5.00, 0, 1, "asdl", "jkl;")
        weight_list_g = [a_u_00, a_u_01, a_o_00, a_o_01, i_u_00, i_o_00,
                         other_0, other_1]
        self.genome_h = genetics.genome(layer_list_a, layer_list_b, weight_list_g,
                                        weight_list_d)
        self.genome_i = genetics.genome(layer_list_a, layer_list_b, weight_list_d,
                                        weight_list_g)
        #case where the extras are for a different layer (both chromosomes)
        #and there's non-matching extra as the end of the layer chromosomes
        other_2 = genetics.weight_gene(5, False, False, 0, "zxcv",
                                      5.00, 0, 0, "zxcv", "bnm,")
        other_3 = genetics.weight_gene(5, False, False, 0, "bnm,",
                                      5.00, 0, 1, "zxcv", "bnm,")
        layer_ka = genetics.layer_gene(5, False, False, 0, "INka",
                                        [], 5, "input")
        layer_list_d = [layer_a, layer_i, layer_concat, layer_u, layer_o, layer_ka]
        weight_list_i = [a_u_00, a_u_01, a_o_00, a_o_01, i_u_00, i_o_00,
                         other_2, other_3]
        self.genome_j = genetics.genome(layer_list_c, layer_list_d, weight_list_i,
                                        weight_list_g)
        self.genome_k = genetics.genome(layer_list_d, layer_list_c, weight_list_g,
                                        weight_list_i)

    def test_last_shared(self):
        n, m = self.genome_a.last_shared()
        self.assertEqual(n, 4)
        self.assertEqual(m, 3)
        n, m = self.genome_b.last_shared()
        #...I *think* this is how I want it
        self.assertEqual(n, 4)
        self.assertEqual(m, 5)
        n, m = self.genome_c.last_shared()
        self.assertEqual(n, 4)
        self.assertEqual(m, 5)
        n, m = self.genome_d.last_shared()
        self.assertEqual(n, 4)
        self.assertEqual(m, 5)
        n, m = self.genome_e.last_shared()
        self.assertEqual(m, 5)
        n, m = self.genome_f.last_shared()
        self.assertEqual(m, 5)
        n, m = self.genome_g.last_shared()
        self.assertEqual(m, 5)
        n, m = self.genome_h.last_shared()
        self.assertEqual(m, 5)
        n, m = self.genome_i.last_shared()
        self.assertEqual(m, 5)
        n, m = self.genome_j.last_shared()
        self.assertEqual(n, 4)
        self.assertEqual(m, 5)
        n, m = self.genome_k.last_shared()
        self.assertEqual(n, 4)
        self.assertEqual(m, 5)
        
    def test_crossover(self):
        #simple test case
        cross_a = self.genome_a.crossover()
        #will crossover at 3, 2
        self.assertEqual(cross_a.layerchr_a[4].nodes, 7)
        self.assertEqual(cross_a.layerchr_b[4].nodes, 5)
        self.assertEqual(cross_a.weightchr_a[3].weight, 7.00)
        self.assertEqual(cross_a.weightchr_b[3].weight, 5.00)
        #crossover at 1, 5
        cross_b = self.genome_b.crossover()
        self.assertEqual(len(cross_b.weightchr_b), 8)
        self.assertEqual(len(cross_b.weightchr_a), 6)
        self.assertEqual(cross_b.weightchr_a[5].ident, "io00")
        self.assertEqual(cross_b.weightchr_b[5].ident, "ao01")
        #and other way around
        cross_c = self.genome_c.crossover()
        self.assertEqual(len(cross_c.weightchr_a), 8)
        self.assertEqual(len(cross_c.weightchr_b), 6)
        cross_d = self.genome_d.crossover()
        self.assertEqual(len(cross_d.layerchr_b), 6)
        self.assertEqual(len(cross_d.layerchr_a), 5)
        self.assertEqual(len(cross_d.weightchr_a), 6)
        self.assertEqual(len(cross_d.weightchr_b), 8)
        cross_e = self.genome_e.crossover()
        self.assertEqual(len(cross_e.layerchr_a), 6)
        self.assertEqual(len(cross_e.layerchr_b), 5)
        self.assertEqual(len(cross_e.weightchr_b), 6)
        self.assertEqual(len(cross_e.weightchr_a), 8)
        #crossover at 2, 2
        cross_f = self.genome_f.crossover()
        self.assertEqual(cross_f.weightchr_b[5].ident, "iu01")
        self.assertEqual(cross_f.weightchr_a[5].ident, "io00")
        #crossover at 1, 4
        cross_g = self.genome_g.crossover()
        self.assertEqual(cross_g.weightchr_a[4].ident, "iu00")
        self.assertEqual(cross_g.weightchr_b[4].ident, "iu00")
        self.assertEqual(cross_g.weightchr_a[5].ident, "iu01")
        self.assertEqual(cross_g.weightchr_b[5].ident, "io00")
        cross_h = self.genome_h.crossover()
        self.assertEqual(len(cross_h.weightchr_a), 6)
        self.assertEqual(len(cross_h.weightchr_b), 8)
        
    def test_recomb(self):
        recomb_a = self.genome_a.recombine(self.genome_a)
        x = 0
        for x in range(len(recomb_a.layerchr_a)):
            self.assertEqual(recomb_a.layerchr_a[x].ident,
                             self.genome_a.layerchr_a[x].ident)
        x = 0
        for x in range(len(recomb_a.layerchr_b)):
            self.assertEqual(recomb_a.layerchr_b[x].ident,
                             self.genome_a.layerchr_b[x].ident)
            x = 0
        for x in range(len(recomb_a.weightchr_a)):
            self.assertEqual(recomb_a.weightchr_a[x].ident,
                             self.genome_a.weightchr_a[x].ident)
            x = 0
        for x in range(len(recomb_a.weightchr_b)):
            self.assertEqual(recomb_a.weightchr_b[x].ident,
                             self.genome_a.weightchr_b[x].ident)
        recomb_b = self.genome_a.recombine(self.genome_k)
        self.assertEqual(len(recomb_b.layerchr_b), 6)
        self.assertEqual(len(recomb_b.layerchr_a), 5)
        self.assertEqual(len(recomb_b.weightchr_a), 4)
        self.assertEqual(len(recomb_b.weightchr_b), 8)
        for gene in recomb_b.weightchr_a:
            for weight in recomb_b.weightchr_b:
                if gene.ident == weight.ident:
                    aru = True
            self.assertTrue(aru)

#tests mating function
class testMating(unittest.TestCase):

    def test_mating(self):
        tak_1 = tako.Tako.default_tako(0, 0, 0)
        tak_2 = tako.Tako.default_tako(0, 0, 1)
        result = tak_1.mated(tak_2)
        self.assertEqual(result, ("boredom", -1))
        tak_1.desire = 150
        result = tak_1.mated(tak_2)
        self.assertEqual(result, ("boredom", -1))
        tak_1.desire = 0
        tak_2.desire = 150
        result = tak_1.mated(tak_2)
        self.assertEqual(result, ("boredom", -1))
        tak_1.desire = 100
        result = tak_1.mated(tak_2)
        self.assertEqual(len(result), 6)
        x = os.path.join("Gen files", "T329-146-643.gen")
        os.remove(x)
        x = os.path.join("Gen files", "T548-403-155.gen")
        os.remove(x)
        

if __name__ == '__main__':
    unittest.main()
