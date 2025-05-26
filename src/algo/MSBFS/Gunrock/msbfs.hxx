#pragma once

#include <gunrock/algorithms/algorithms.hxx>
#include <vector>

namespace gunrock {
	namespace bfs {

		template<typename vertex_t>
		struct param_t {
			std::vector<vertex_t> sources;

			param_t(const std::vector<vertex_t> &_sources) : sources(_sources) {
			}
		};

		template<typename vertex_t>
		struct result_t {
			vertex_t *distances;
			vertex_t *predecessors;

			result_t(vertex_t *_distances, vertex_t *_predecessors) : distances(_distances), predecessors(_predecessors) {
			}
		};

		template<typename graph_t, typename param_type, typename result_type>
		struct problem_t : gunrock::problem_t<graph_t> {
			param_type param;
			result_type result;

			problem_t(graph_t &G, param_type &_param, result_type &_result, std::shared_ptr<gcuda::multi_context_t> _context)
				: gunrock::problem_t<graph_t>(G, _context), param(_param), result(_result) {
			}

			using vertex_t = typename graph_t::vertex_type;
			using edge_t = typename graph_t::edge_type;
			using weight_t = typename graph_t::weight_type;

			void init() override {
			}

			void reset() override {
				auto num_vertices = this->get_graph().get_number_of_vertices();
				auto batch_size = param.sources.size();

				auto d_predecessors = thrust::device_pointer_cast(this->result.predecessors);
				auto d_distances = thrust::device_pointer_cast(this->result.distances);

				thrust::fill(thrust::device, d_predecessors, d_predecessors + batch_size * num_vertices, -1);
				thrust::fill(thrust::device, d_distances, d_distances + batch_size * num_vertices,
							 std::numeric_limits<vertex_t>::max());

				for (int i = 0; i < batch_size; ++i) {
					vertex_t s = this->param.sources[i];
					d_predecessors[i * num_vertices + s] = s;
					d_distances[i * num_vertices + s] = 0;
				}
			}
		};

		template<typename problem_t>
		struct enactor_t : gunrock::enactor_t<problem_t> {
			enactor_t(problem_t *_problem, std::shared_ptr<gcuda::multi_context_t> _context)
				: gunrock::enactor_t<problem_t>(_problem, _context) {
			}

			using vertex_t = typename problem_t::vertex_t;
			using edge_t = typename problem_t::edge_t;
			using weight_t = typename problem_t::weight_t;
			using frontier_t = typename enactor_t<problem_t>::frontier_t;

			void prepare_frontier(frontier_t *f, gcuda::multi_context_t &context) override {
				auto P = this->get_problem();
				for (size_t i = 0; i < P->param.sources.size(); ++i) {
					f->push_back(P->param.sources[i]);
				}
			}

			void loop(gcuda::multi_context_t &context) override {
				auto E = this->get_enactor();
				auto P = this->get_problem();
				auto G = P->get_graph();

				auto distances = P->result.distances;
				auto predecessors = P->result.predecessors;
				auto batch_size = P->param.sources.size();
				auto num_vertices = G.get_number_of_vertices();
				auto iteration = this->iteration;

				auto search = [=] __host__ __device__(
									  vertex_t const &source,
									  vertex_t const &neighbor,
									  edge_t const &edge,
									  weight_t const &weight) -> bool {
					bool updated = false;
					for (int batch = 0; batch < batch_size; ++batch) {
						vertex_t *dist_row = distances + batch * num_vertices;
						vertex_t *pred_row = predecessors + batch * num_vertices;

						vertex_t new_dist = dist_row[source] + 1;
						vertex_t old_dist = gunrock::math::atomic::min(&dist_row[neighbor], new_dist);
						if (new_dist < old_dist) {
							gunrock::math::atomic::cas(&pred_row[neighbor], static_cast<vertex_t>(-1), source);
							updated = true;
						}
					}
					return updated;
				};

				gunrock::operators::advance::execute<
						gunrock::operators::load_balance_t::block_mapped>(
						G, E, search, context);
			}
		};

		template<typename graph_t>
		float run(graph_t &G, std::vector<typename graph_t::vertex_type> &sources, typename graph_t::vertex_type *distances,
				  typename graph_t::vertex_type *predecessors,
				  std::shared_ptr<gcuda::multi_context_t> context =
						  std::shared_ptr<gcuda::multi_context_t>(new gcuda::multi_context_t(0))) {
			using vertex_t = typename graph_t::vertex_type;
			using param_type = param_t<vertex_t>;
			using result_type = result_t<vertex_t>;

			param_type param(sources);
			result_type result(distances, predecessors);

			using problem_type = problem_t<graph_t, param_type, result_type>;
			using enactor_type = enactor_t<problem_type>;

			problem_type problem(G, param, result, context);
			problem.init();
			problem.reset();

			enactor_type enactor(&problem, context);
			return enactor.enact();
		}

	}// namespace bfs
}// namespace gunrock